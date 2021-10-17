import asyncio
import base64
import json
import logging
import os
from datetime import datetime
from http.cookies import SimpleCookie
from typing import *

import aiohttp
from yarl import URL

from . import errors
from .constants import LANGS
from .models import *
from .paginator import (
    DailyRewardPaginator,
    MergedTransactions,
    MergedWishHistory,
    Transactions,
    WishHistory,
)
from .utils import (
    create_short_lang_code,
    extract_authkey,
    generate_cn_dynamic_secret,
    generate_dynamic_secret,
    get_authkey,
    get_banner_ids,
    get_browser_cookies,
    permanent_cache,
    recognize_server,
)

__all__ = ["GenshinClient", "MultiCookieClient", "ChineseClient", "ChineseMultiCookieClient"]


class GenshinClient:
    """A simple http client for genshin endpoints"""

    DS_SALT = "6cqshh5dhw73bzxn20oexa9k516chk7s"
    ACT_ID = "e202102251931481"

    WEBSTATIC_URL = "https://webstatic-sea.mihoyo.com/"
    TAKUMI_URL = "https://api-os-takumi.mihoyo.com/"
    RECORD_URL = "https://api-os-takumi.mihoyo.com/game_record/"
    REWARD_URL = "https://hk4e-api-os.mihoyo.com/event/sol/"
    GACHA_INFO_URL = "https://hk4e-api-os.mihoyo.com/event/gacha_info/api/"
    YSULOG_URL = "https://hk4e-api-os.mihoyo.com/ysulog/api/"
    MAP_URL = "https://api-os-takumi-static.mihoyo.com/common/map_user/ys_obc/v1/map/"
    STATIC_MAP_URL = "https://api-os-takumi-static.mihoyo.com/common/map_user/ys_obc/v1/map"

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"  # noqa: E501

    _session: Optional[aiohttp.ClientSession] = None
    logger: logging.Logger = logging.getLogger(__name__)

    cache: Optional[MutableMapping[Tuple[Any, ...], Any]] = None
    paginator_cache: Optional[MutableMapping[Tuple[Any, ...], Any]] = None
    static_cache: ClassVar[MutableMapping[str, Any]] = {}
    _permanent_cache: ClassVar[MutableMapping[Any, Any]] = {}  # NEVER CHANGE!

    def __init__(
        self,
        cookies: Mapping[str, str] = None,
        authkey: str = None,
        *,
        lang: str = "en-us",
        debug: bool = False,
    ) -> None:
        """Create a new GenshinClient instance by setting the language and authentication

        If debug is turned on the logger for GenshinClient will be turned to debug mode.
        """
        if cookies:
            self.cookies = cookies

        self.authkey = authkey
        self.lang = lang

        if debug:
            logging.basicConfig()
            logging.getLogger("genshin").setLevel(logging.DEBUG)

    # PROPERTIES:

    @property
    def session(self) -> aiohttp.ClientSession:
        """The current client session, created when needed"""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        return self._session

    @property
    def cookies(self) -> Mapping[str, str]:
        """The cookie jar belonging to the current session"""
        return {cookie.key: cookie.value for cookie in self.session.cookie_jar}

    @cookies.setter
    def cookies(self, cookies: Mapping[str, Any]) -> None:
        cks = {str(key): value for key, value in cookies.items()}
        self.session.cookie_jar.clear()
        self.session.cookie_jar.update_cookies(cks)

    @property
    def hoyolab_uid(self) -> Optional[int]:
        """The logged-in user's hoyolab uid"""
        for cookie in self.session.cookie_jar:
            if cookie.key in ("ltuid", "account_id"):
                return int(cookie.value)

        return None

    @property
    def lang(self) -> str:
        """The default language, defaults to en-us"""
        return self._lang

    @lang.setter
    def lang(self, lang: str) -> None:
        if lang not in LANGS:
            raise ValueError(f"{lang} is not a valid language, must be one of: " + ", ".join(LANGS))

        self._lang = lang

    @property
    def authkey(self) -> Optional[str]:
        """The default authkey"""
        return self._authkey

    @authkey.setter
    def authkey(self, authkey: Optional[str]) -> None:
        if authkey is not None:
            try:
                base64.b64decode(authkey, validate=True)
            except Exception as e:
                raise ValueError("authkey is not a valid base64 encoded string") from e

            if len(authkey) != 1024:
                raise ValueError("authkey must have precisely 1024 characters")

        self._authkey = authkey

    def set_cookies(
        self, cookies: Union[Mapping[str, Any], str] = None, **kwargs: Any
    ) -> Mapping[str, str]:
        """Helper cookie setter that accepts cookie headers"""
        if not bool(cookies) ^ bool(kwargs):
            raise TypeError("Cannot use both positional and keyword arguments at once")

        cookies = cookies or kwargs
        cookies = {morsel.key: morsel.value for morsel in SimpleCookie(cookies).values()}
        self.cookies = cookies
        return self.cookies

    def set_browser_cookies(self, browser: str = None) -> Mapping[str, str]:
        """Extract cookies from your browser and set them as client cookies

        Refer to get_browser_cookies for more info.
        """
        self.cookies = get_browser_cookies(browser)
        return self.cookies

    def set_authkey(self, authkey: str = None) -> None:
        """Sets an authkey for wish & transaction logs

        Accepts an authkey, a url containing an authkey or a path to a file with an authkey.
        """
        if authkey is None or os.path.isfile(authkey):
            authkey = get_authkey(authkey)
        else:
            authkey = extract_authkey(authkey) or authkey

        self.authkey = authkey

    def set_cache(
        self,
        maxsize: int,
        strategy: Literal["FIFO", "LFU", "LRU", "MRU", "RR"] = "LRU",
        *,
        ttl: int = None,
        getsizeof: Callable[[Any], float] = None,
    ) -> MutableMapping[Any, Any]:
        """Create and set a new cache (not static or paginator)

        If ttl is set then a TTL cache is created
        """
        import cachetools

        if ttl:
            if strategy != "LRU":
                raise ValueError("TTL caches must use LRU")

            self.cache = cachetools.TTLCache(maxsize, ttl, getsizeof=getsizeof)
            return self.cache
        elif strategy == "TTL":
            raise ValueError("TTL caches should be set using the ttl kwarg")

        cls_name = strategy + "Cache"
        if not hasattr(cachetools, cls_name):
            raise ValueError(f"Invalid strategy: {strategy}")

        self.cache = getattr(cachetools, cls_name)(maxsize, getsizeof=getsizeof)
        return self.cache

    def _check_cache(
        self, key: Tuple[Any, ...], check: Callable[[Any], bool] = None, *, lang: str = None
    ) -> Optional[Any]:
        """Check the cache for any entries"""
        if self.cache is None:
            return None

        key = key + (lang or self.lang,)

        if key not in self.cache:
            return None

        data = self.cache[key]
        if check is None or check(data):
            return data

        del self.cache[key]
        return None

    def _update_cache(
        self,
        data: Any,
        key: Tuple[Any, ...],
        check: Callable[[Any], bool] = None,
        *,
        lang: str = None,
    ) -> None:
        """Update the cache with a new entry"""
        if self.cache is None:
            return

        key = key + (lang or self.lang,)

        if check is None or check(data):
            self.cache[key] = data

    # ASYNCIO HANDLERS:

    async def close(self) -> None:
        """Close the client's session"""
        if not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        await self.close()

    # RAW HTTP REQUESTS:

    async def request(
        self,
        url: Union[str, URL],
        method: str = "GET",
        *,
        headers: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request and return a parsed dictionary response"""
        headers = headers or {}
        headers["user-agent"] = self.USER_AGENT

        async with self.session.request(method, url, headers=headers, **kwargs) as r:
            data = await r.json()

        if data["retcode"] == 0:
            return data["data"]

        errors.raise_for_retcode(data)

    async def request_webstatic(
        self,
        url: Union[str, URL],
        *,
        headers: Dict[str, Any] = None,
        cache: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Request a static json file"""
        if cache and str(url) in self.static_cache:
            return self.static_cache[str(url)]

        headers = headers or {}
        headers["user-agent"] = self.USER_AGENT

        url = URL(self.WEBSTATIC_URL).join(URL(url))

        self.logger.debug(f"STATIC {url}")

        async with self.session.get(url, headers=headers, **kwargs) as r:
            data = await r.json()

        if cache:
            self.static_cache[str(url)] = data

        return data

    async def request_hoyolab(
        self,
        endpoint: Union[str, URL],
        *,
        method: str = "GET",
        lang: str = None,
        cache: Tuple[Any, ...] = None,
        cache_check: Callable[[Any], bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards misc hoyolabs api

        Community related data
        """
        if cache:
            data = self._check_cache(cache, cache_check, lang=lang)
            if data:
                return data

        if not self.cookies:
            raise RuntimeError("No cookies provided")
        if lang not in LANGS and lang is not None:
            raise ValueError(f"{lang} is not a valid language, must be one of: " + ", ".join(LANGS))

        url = URL(self.TAKUMI_URL).join(URL(endpoint))

        headers = {
            "x-rpc-app_version": "1.5.0",
            "x-rpc-client_type": "4",
            "x-rpc-language": lang or self.lang,
            "ds": generate_dynamic_secret(self.DS_SALT),
        }

        debug_url = url.with_query(kwargs.get("params", {}))
        self.logger.debug(f"RECORD {method} {debug_url}")

        data = await self.request(url, method, headers=headers, **kwargs)

        if cache:
            self._update_cache(data, cache, cache_check, lang=lang)

        return data

    async def request_game_record(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        cache: Tuple[Any, ...] = None,
        cache_check: Callable[[Any], bool] = None,
        **kwargs: Any,
    ):
        """Make a request towards the game record endpoint

        User stats related data
        """
        # this is simply just an alias for shorter request endpoints
        url = URL(self.RECORD_URL).join(URL(endpoint))

        return await self.request_hoyolab(
            url, method=method, cache=cache, cache_check=cache_check, **kwargs
        )

    async def request_daily_reward(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: str = None,
        params: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the daily reward endpoint

        Daily reward claiming and history
        """

        params = params or {}
        if not self.cookies:
            raise RuntimeError("No cookies provided")

        url = URL(self.REWARD_URL).join(URL(endpoint))

        params["lang"] = lang or self.lang
        params["act_id"] = self.ACT_ID

        self.logger.debug(f"DAILY {method} {url.with_query(params)}")

        return await self.request(url, method, params=params, **kwargs)

    async def request_gacha_info(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: str = None,
        authkey: str = None,
        params: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the game info endpoint

        Wish history related data
        """
        params = params or {}

        base_url = URL(self.GACHA_INFO_URL)
        url = base_url.join(URL(endpoint))

        params["authkey_ver"] = 1
        params["authkey"] = authkey or self.authkey
        params["lang"] = create_short_lang_code(lang or self.lang)

        if authkey is None and self.authkey is None:
            raise RuntimeError("No authkey provided")

        debug_url = url.with_query({k: v for k, v in params.items() if k != "authkey"})
        self.logger.debug(f"GACHA {method} {debug_url}")

        return await self.request(url, method, params=params, **kwargs)

    async def request_transaction(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: str = None,
        authkey: str = None,
        params: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the transaction log endpoint

        Transaction related data
        """
        params = params or {}

        base_url = URL(self.YSULOG_URL)
        url = base_url.join(URL(endpoint))

        params["authkey_ver"] = 1
        params["sign_type"] = 2
        params["authkey"] = authkey or self.authkey
        params["lang"] = create_short_lang_code(lang or self.lang)

        if authkey is None and self.authkey is None:
            raise RuntimeError("No authkey provided")

        debug_url = url.with_query({k: v for k, v in params.items() if k != "authkey"})
        self.logger.debug(f"TRANS {method} {debug_url}")

        return await self.request(url, method, params=params, **kwargs)

    async def request_map(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: str = None,
        map_id: int = 2,
        static: bool = False,
        params: Dict[str, Any] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make a request towards the map endpoint

        Interactive map related data
        """
        params = params or {}

        base_url = self.STATIC_MAP_URL if static else self.MAP_URL
        url = URL(base_url).join(URL(endpoint))

        params["map_id"] = map_id
        params["app_sn"] = "ys_obc"
        params["lang"] = lang or self.lang

        return await self.request(url, method, params=params, **kwargs)

    # HOYOLAB:

    async def genshin_accounts(self, *, lang: str = None) -> List[GenshinAccount]:
        """Get the genshin accounts of the currently logged-in user"""
        # fmt: off
        data = await self.request_hoyolab(
            "binding/api/getUserGameRolesByCookie",
            lang=lang,
            cache=("accounts", self.hoyolab_uid)
        )
        # fmt: on
        return [GenshinAccount(**i) for i in data["list"]]

    async def search_users(self, keyword: str, *, lang: str = None) -> List[SearchUser]:
        data = await self.request_hoyolab(
            "community/apihub/wapi/search",
            lang=lang,
            params=dict(keyword=keyword, size=20, gids=2),
            cache=("search", keyword),
        )
        return [SearchUser(**i) for i in data["users"]]

    async def set_visibility(self, public: bool) -> None:
        """Sets your data to public or private."""
        await self.request_game_record(
            "genshin/wapi/publishGameRecord",
            method="POST",
            json=dict(is_public=public, game_id=2),
        )

    async def get_recommended_users(self, *, limit: int = 200) -> List[SearchUser]:
        """Get a list of recommended active users"""
        data = await self.request_hoyolab(
            "community/user/wapi/recommendActive",
            params=dict(page_size=limit),
        )
        return [SearchUser(**i["user"]) for i in data["list"]]

    async def redeem_code(self, code: str, uid: int = None, *, lang: str = None) -> None:
        """Redeems a gift code for the current user"""
        # do note that this endpoint is very quirky, can't really make this pretty
        if uid is not None:
            server = recognize_server(uid)
            lang = create_short_lang_code(lang or self.lang)
            await self.request(
                "https://hk4e-api-os.mihoyo.com/common/apicdkey/api/webExchangeCdkey",
                params=dict(
                    uid=uid,
                    region=server,
                    cdkey=code,
                    game_biz="hk4e_global",
                    lang=lang,
                ),
            )
            return

        accounts = [a for a in await self.genshin_accounts() if a.level >= 10]

        for i, account in enumerate(accounts):
            # there's a ratelimit of 1 request every 5 seconds
            if i:
                await asyncio.sleep(5)

            await self.redeem_code(code, account.uid, lang=lang)

    # GAME RECORD:

    async def get_record_card(self, hoyolab_uid: int = None, *, lang: str = None) -> RecordCard:
        """Get a user's record card. If a uid is not provided gets the logged in user's"""
        data = await self.request_game_record(
            "card/wapi/getGameRecordCard",
            lang=lang,
            params=dict(uid=hoyolab_uid or self.hoyolab_uid, gids=2),
            cache=("record", hoyolab_uid),
            cache_check=lambda data: len(data["list"]) > 0,
        )
        cards = data["list"]
        if not cards:
            raise errors.DataNotPublic({})

        return RecordCard(**cards[0])

    async def get_user(self, uid: int, *, lang: str = None) -> UserStats:
        """Get a user's stats and characters"""
        server = recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/index",
            lang=lang,
            params=dict(role_id=uid, server=server),
            cache=("user", uid),
        )

        character_ids = [char["id"] for char in data["avatars"]]
        character_data = await self.request_game_record(
            "genshin/api/character",
            method="POST",
            lang=lang,
            json=dict(character_ids=character_ids, role_id=uid, server=server),
            cache=("characters", uid),
        )
        data.update(character_data)

        return UserStats(**data)

    async def get_partial_user(self, uid: int, *, lang: str = None) -> PartialUserStats:
        """Helper alternative function to get a user without any equipment"""
        server = recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/index",
            lang=lang,
            params=dict(server=server, role_id=uid),
            cache=("user", uid),
        )
        return PartialUserStats(**data)

    async def get_characters(
        self, uid: int, character_ids: List[int], *, lang: str = None
    ) -> List[Character]:
        """Helper function to fetch characters from just their ids"""
        server = recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/character",
            method="POST",
            lang=lang,
            json=dict(character_ids=character_ids, role_id=uid, server=server),
            cache=("characters", uid),
        )
        return [Character(**i) for i in data["avatars"]]

    async def get_spiral_abyss(self, uid: int, *, previous: bool = False) -> SpiralAbyss:
        """Get spiral abyss runs"""
        server = recognize_server(uid)
        schedule_type = 2 if previous else 1
        data = await self.request_game_record(
            "genshin/api/spiralAbyss",
            params=dict(role_id=uid, server=server, schedule_type=schedule_type),
            cache=("abyss", uid, schedule_type),
        )
        return SpiralAbyss(**data)

    async def get_activities(self, uid: int, *, lang: str = None) -> Activities:
        """Get activities"""
        server = recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/activities",
            lang=lang,
            params=dict(server=server, role_id=uid),
            cache=("activities", uid),
        )
        return Activities(**data["activities"][0])

    async def get_full_user(self, uid: int, *, lang: str = None) -> FullUserStats:
        """Get a user with all their possible data"""
        user, abyss1, abyss2, activities = await asyncio.gather(
            self.get_user(uid, lang=lang),
            self.get_spiral_abyss(uid, previous=False),
            self.get_spiral_abyss(uid, previous=True),
            self.get_activities(uid, lang=lang),
        )
        abyss = {"current": abyss1, "previous": abyss2}
        return FullUserStats(**user.dict(), abyss=abyss, activities=activities)

    # DAILY REWARDS:

    async def get_reward_info(self, *, lang: str = None) -> DailyRewardInfo:
        """Get the daily reward info for the current user"""
        data = await self.request_daily_reward("info", lang=lang)
        return DailyRewardInfo(data["is_sign"], data["total_sign_day"])

    @permanent_cache(
        lambda self, lang=None: ("rewards", datetime.utcnow().month, lang or self.lang)
    )
    async def get_monthly_rewards(self, *, lang: str = None) -> List[DailyReward]:
        """Get a list of all availible rewards for the current month"""
        data = await self.request_daily_reward("home", lang=lang)
        return [DailyReward(**i) for i in data["awards"]]

    def claimed_rewards(self, *, limit: int = None, lang: str = None) -> DailyRewardPaginator:
        """Get all claimed rewards for the current user

        NOTE: Mihoyo does not support languages on this endpoint yet
        """
        return DailyRewardPaginator(self, limit=limit, lang=lang)

    @overload
    async def claim_daily_reward(
        self, *, lang: str = None, reward: Literal[True] = ...
    ) -> DailyReward:
        ...

    @overload
    async def claim_daily_reward(self, *, lang: str = None, reward: Literal[False]) -> None:
        ...

    async def claim_daily_reward(
        self, *, lang: str = None, reward: bool = True
    ) -> Optional[DailyReward]:
        """Signs into hoyolab and claims the daily reward.

        If reward is True then the claimed reward will be returned
        """
        await self.request_daily_reward("sign", method="POST", lang=lang)

        if reward:
            info, rewards = await asyncio.gather(
                self.get_reward_info(lang=lang),
                self.get_monthly_rewards(lang=lang),
            )
            return rewards[info.claimed_rewards - 1]

    # WISH HISTORY:

    @overload
    def wish_history(
        self,
        banner_type: None = ...,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> MergedWishHistory:
        ...

    @overload
    def wish_history(
        self,
        banner_type: Union[int, BannerType],
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> WishHistory:
        ...

    def wish_history(
        self,
        banner_type: Union[int, BannerType] = None,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> Union[WishHistory, MergedWishHistory]:
        """Get the wish history of a user"""
        if banner_type is None:
            return MergedWishHistory(self, lang=lang, authkey=authkey, limit=limit, end_id=end_id)
        else:
            return WishHistory(
                self,
                banner_type,
                lang=lang,
                authkey=authkey,
                limit=limit,
                end_id=end_id,
            )

    @permanent_cache(lambda self, lang=None, authkey=None: ("banners", lang or self.lang))
    async def get_banner_names(self, *, lang: str = None, authkey: str = None) -> Dict[int, str]:
        """Get a list of banner names"""
        data = await self.request_gacha_info(
            "getConfigList",
            lang=lang,
            authkey=authkey,
        )
        return {int(i["key"]): i["name"] for i in data["gacha_type_list"]}

    async def get_banner_details(self, banner_id: str, *, lang: str = None) -> BannerDetails:
        """Get details of a specific banner using its id"""
        data = await self.request_webstatic(
            f"/hk4e/gacha_info/os_asia/{banner_id}/{lang or self.lang}.json"
        )
        return BannerDetails(**data)

    async def get_all_banner_details(
        self, banner_ids: List[str] = None, *, lang: str = None
    ) -> List[BannerDetails]:
        """Get all banner details at once in a batch"""
        banner_ids = banner_ids or get_banner_ids()
        data = await asyncio.gather(*(self.get_banner_details(i, lang=lang) for i in banner_ids))
        return list(data)

    async def get_gacha_items(self, *, lang: str = None) -> List[GachaItem]:
        """Get the list of characters and weapons that can be gotten from the gacha."""
        data = await self.request_webstatic(
            f"/hk4e/gacha_info/os_asia/items/{lang or self.lang}.json"
        )
        return [GachaItem(**i) for i in data]

    # TRANSACTIONS:

    async def _get_transaction_reasons(self, lang: str) -> Dict[str, str]:
        """Get a mapping of transaction reasons"""
        base = "https://mi18n-os.mihoyo.com/webstatic/admin/mi18n/hk4e_global/"
        data = await self.request_webstatic(base + f"m02251421001311/m02251421001311-{lang}.json")

        return {
            k.split("_")[-1]: v
            for k, v in data.items()
            if k.startswith("selfinquiry_general_reason_")
        }

    @overload
    def transaction_log(
        self,
        kind: None = ...,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> MergedTransactions:
        ...

    @overload
    def transaction_log(
        self,
        kind: Literal["primogem", "crystal", "resin"],
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> Transactions[Transaction]:
        ...

    @overload
    def transaction_log(
        self,
        kind: Literal["artifact", "weapon"],
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> Transactions[ItemTransaction]:
        ...

    def transaction_log(
        self,
        kind: Literal["primogem", "crystal", "resin", "artifact", "weapon"] = None,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> Union[Transactions, MergedTransactions]:
        # TODO: Utilize the new diary
        if kind is None:
            return MergedTransactions(self, lang=lang, authkey=authkey, limit=limit, end_id=end_id)
        else:
            return Transactions(self, kind, lang=lang, authkey=authkey, limit=limit, end_id=end_id)

    # INTERACTIVE MAP:

    async def _get_map_pin_icons(self, map_id: int = 2, *, lang: str = None) -> Dict[int, str]:
        data = await self.request_map("spot_kind/get_icon_list", lang=lang, map_id=map_id)
        return {i["id"]: i["url"] for i in data["icons"]}

    async def get_map_info(self, map_id: int = 2, *, lang: str = None) -> MapInfo:
        """Get info about an interactive map"""
        data = await self.request_map(
            "map/info",
            lang=lang,
            map_id=map_id,
            static=True,
        )
        return MapInfo(**data["info"])

    async def get_map_labels(self, map_id: int = 2, *, lang: str = None) -> List[MapNode]:
        """Get the map tree of all categories & lables of map points"""
        data = await self.request_map("map/label/tree", lang=lang, map_id=map_id, static=True)
        return [MapNode(**i) for i in data["tree"]]

    async def get_map_points(
        self, map_id: int = 2, *, lang: str = None
    ) -> Tuple[List[MapNode], List[MapPoint]]:
        """Get a tuple of all map lables and map points"""
        data = await self.request_map("map/point/list", lang=lang, map_id=map_id, static=True)

        labels = [MapNode(**i) for i in data["label_list"]]
        points = [MapPoint(**i) for i in data["point_list"]]

        return labels, points

    async def get_map_locations(self, map_id: int = 2, *, lang: str = None) -> List[MapLocation]:
        """Get a list of all locations on a map"""
        data = await self.request_map("map/map_anchor/list", lang=lang, map_id=map_id, static=True)

        return [MapLocation(**i) for i in data["list"]]

    # MISC:

    async def init(self, lang: str = None):
        """Request all static endpoints to not require them later"""
        lang = lang or self.lang

        try:
            banner_ids = get_banner_ids()
        except FileNotFoundError:
            banner_ids = []

        await asyncio.gather(
            self.get_banner_names(lang=lang),
            self._get_transaction_reasons(lang=lang),
            self.get_all_banner_details(banner_ids, lang=lang),
        )

    async def fetch_banner_ids(self) -> List[str]:
        """Fetch banner ids from a user-mantained repo"""
        url = "https://raw.githubusercontent.com/thesadru/genshin.py/gh-pages/banner_ids.txt"
        async with self.session.get(url) as r:
            data = await r.text()
        return data.splitlines()


class ChineseClient(GenshinClient):
    """A Genshin Client for chinese endpoints"""

    DS_SALT = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
    ACT_ID = "e202009291139501"

    TAKUMI_URL = "https://api-takumi.mihoyo.com/"
    RECORD_URL = "https://api-takumi.mihoyo.com/game_record/app/"
    REWARD_URL = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/"
    MAP_URL = "https://api-takumi-static.mihoyo.com/common/map_user/ys_obc/v1/map/"
    STATIC_MAP_URL = "https://api-static.mihoyo.com/common/map_user/ys_obc/v1/map"

    def __init__(
        self,
        cookies: Mapping[str, str] = None,
        authkey: str = None,
        *,
        lang: str = "zh-tw",
        debug: bool = False,
    ) -> None:
        super().__init__(cookies=cookies, authkey=authkey, lang=lang, debug=debug)

    async def request_hoyolab(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: str = None,
        json: Any = None,
        params: Dict[str, Any] = None,
        cache: Tuple[Any, ...] = None,
        cache_check: Callable[[Any], bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        params = params or {}

        if cache:
            data = self._check_cache(cache, cache_check, lang=lang)
            if data:
                return data

        if not self.cookies:
            raise RuntimeError("No cookies provided")
        if lang not in LANGS and lang is not None:
            raise ValueError(f"{lang} is not a valid language, must be one of: " + ", ".join(LANGS))

        url = URL(self.TAKUMI_URL).join(URL(endpoint))

        # all of this repetition is literally just to change these few lines
        headers = {
            "x-rpc-app_version": "2.11.1",
            "x-rpc-client_type": "5",
            "x-rpc-language": lang or self.lang,
            "ds": generate_cn_dynamic_secret(self.DS_SALT, json, params),
        }

        debug_url = url.with_query(kwargs.get("params", {}))
        self.logger.debug(f"RECORD {method} {debug_url}")

        data = await self.request(url, method, headers=headers, json=json, params=params, **kwargs)

        if cache:
            self._update_cache(data, cache, cache_check, lang=lang)

        return data

    async def get_daily_note(self, uid: int, *, lang: str = None) -> Any:
        server = recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/dailyNote",
            lang=lang,
            params=dict(server=server, role_id=uid),
            cache=("user", uid),
        )
        return data

    @overload
    async def claim_daily_reward(
        self, *, lang: str = None, reward: Literal[True] = ...
    ) -> DailyReward:
        ...

    @overload
    async def claim_daily_reward(self, *, lang: str = None, reward: Literal[False]) -> None:
        ...

    async def claim_daily_reward(
        self, uid: int = None, *, lang: str = None, reward: bool = True
    ) -> Optional[DailyReward]:
        """Signs into hoyolab and claims the daily reward.

        If reward is True then the claimed reward will be returned
        """
        params = {}
        if uid is None:
            accounts = await self.genshin_accounts(lang=lang)
            params["game_uid"] = accounts[0].uid
            params["region"] = accounts[0].server
        else:
            params["game_uid"] = uid
            params["region"] = recognize_server(uid)

        if reward:
            info, rewards = await asyncio.gather(
                self.get_reward_info(lang=lang),
                self.get_monthly_rewards(lang=lang),
            )
            return rewards[info.claimed_rewards - 1]


class MultiCookieClient(GenshinClient):
    """A Genshin Client which allows setting multiple cookies"""

    sessions: List[aiohttp.ClientSession]

    def __init__(
        self,
        cookie_list: Iterable[Mapping[str, str]] = None,
        lang: str = "en-us",
        *,
        debug: bool = False,
    ) -> None:
        self.sessions = []

        if cookie_list:
            self.set_cookies(cookie_list)

        super().__init__(lang=lang, debug=debug)

    @property
    def session(self) -> aiohttp.ClientSession:
        """The current chosen session"""
        if not self.sessions:
            return aiohttp.ClientSession()

        return self.sessions[0]

    @property
    def cookies(self) -> List[Mapping[str, str]]:
        """A list of all cookies"""
        return [{m.key: m.value for m in s.cookie_jar} for s in self.sessions]

    @cookies.setter
    def cookies(self, cookies: List[Mapping[str, Any]]) -> None:
        self.set_cookies(cookies)

    def set_cookies(
        self, cookie_list: Union[Iterable[Union[Mapping[str, Any], str]], str], clear: bool = True
    ) -> None:
        if clear:
            self.sessions.clear()

        if isinstance(cookie_list, str):
            with open(cookie_list) as file:
                cookie_list = json.load(file)

            if not isinstance(cookie_list, list):
                raise RuntimeError("Json file must contain a list of cookies")

        for cookies in cookie_list:
            session = aiohttp.ClientSession(cookies=SimpleCookie(cookies))
            self.sessions.append(session)

    def set_browser_cookies(self, *args: Any, **kwargs: Any) -> NoReturn:
        """Helper overwrite to prevent nasty bugs"""
        raise RuntimeError(f"{type(self).__name__} does not support browser cookies")

    async def close(self) -> None:
        tasks = [
            asyncio.create_task(session.close()) for session in self.sessions if not session.closed
        ]
        await asyncio.wait(tasks)

    async def request(
        self, url: Union[str, URL], method: str = "GET", **kwargs: Any
    ) -> Dict[str, Any]:

        for _ in range(len(self.sessions)):
            try:
                return await super().request(url, method=method, **kwargs)
            except errors.TooManyRequests:
                # move the ratelimited session to the end to let the ratelimit wear off
                session = self.sessions.pop(0)
                self.sessions.append(session)

        # if we're here it means we used up all our sessions so we must handle that
        msg = "All cookies have hit their request limit of 30 accounts per day."
        raise errors.TooManyRequests({}, msg)

    async def request_daily_reward(self, *args: Any, **kwargs: Any) -> NoReturn:
        """Helper overwrite to prevent nasty bugs"""
        raise RuntimeError(f"{type(self).__name__} does not support daily reward endpoints")


class ChineseMultiCookieClient(ChineseClient, MultiCookieClient):
    """A Genshin Client for chinese endpoints which allows setting multiple cookies"""
