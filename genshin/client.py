"""A client interacting directly with the api"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import uuid
import warnings
from datetime import datetime
from http.cookies import SimpleCookie
from typing import *
from urllib.parse import unquote

import aiohttp
from yarl import URL

from . import errors
from .constants import CHARACTER_NAMES, LANGS
from .models import *
from .paginator import *
from .utils import *

__all__ = [
    "GenshinClient",
    "MultiCookieClient",
    "ChineseClient",
    "ChineseMultiCookieClient",
]


class GenshinClient:
    """A simple http client for genshin endpoints

    :var logger: A logger used for debugging
    :var cache: A cache for http requests
    :var paginator_cache: A high-frequency access cache for paginators
    """

    DS_SALT = "6cqshh5dhw73bzxn20oexa9k516chk7s"
    ACT_ID = "e202102251931481"

    WEBSTATIC_URL = "https://webstatic-sea.mihoyo.com/"
    TAKUMI_URL = "https://api-os-takumi.mihoyo.com/"
    RECORD_URL = "https://bbs-api-os.mihoyo.com/game_record/"
    INFO_LEDGER_URL = "https://hk4e-api-os.mihoyo.com/event/ysledgeros/month_info"
    DETAIL_LEDGER_URL = "https://hk4e-api-os.mihoyo.com/event/ysledgeros/month_detail"
    CALCULATOR_URL = "https://sg-public-api.mihoyo.com/event/calculateos/"
    REWARD_URL = "https://hk4e-api-os.mihoyo.com/event/sol/"
    GACHA_INFO_URL = "https://hk4e-api-os.mihoyo.com/event/gacha_info/api/"
    YSULOG_URL = "https://hk4e-api-os.mihoyo.com/ysulog/api/"
    MAP_URL = "https://api-os-takumi-static.mihoyo.com/common/map_user/ys_obc/v1/map/"
    STATIC_MAP_URL = "https://api-os-takumi-static.mihoyo.com/common/map_user/ys_obc/v1/map"

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"  # noqa: E501

    _session: Optional[aiohttp.ClientSession] = None
    _uid: Optional[int] = None
    logger: logging.Logger = logging.getLogger(__name__)

    cache: Optional[MutableMapping[Tuple[Any, ...], Any]] = None
    paginator_cache: Optional[MutableMapping[Tuple[Any, ...], Any]] = None

    fetched_mi18n: bool = False

    def __init__(
        self,
        cookies: Mapping[str, str] = None,
        authkey: str = None,
        *,
        lang: str = "en-us",
        debug: bool = False,
    ) -> None:
        """Create a new GenshinClient instance

        :param cookies: The cookies used for authenticaation
        :param authkey: The authkey used for paginators
        :param lang: The default language
        :param debug: Whether debug logs should be shown in stdout
        """
        if cookies:
            self.cookies = cookies

        self.authkey = authkey
        self.lang = lang
        self.debug = debug

    def __repr__(self) -> str:
        return f"<{type(self).__name__} lang={self.lang!r} hoyolab_uid={self.hoyolab_uid} debug={self.debug}>"

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
    def uid(self) -> Optional[int]:
        return self._uid

    @uid.setter
    def uid(self, uid: Any) -> None:
        if not str(uid).isdigit() or len(str(uid)) != 9:
            raise TypeError(f"Invalid uid: {uid}")

        self._uid = int(uid)

    @property
    def lang(self) -> str:
        """The default language, defaults to "en-us" """
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
            authkey = unquote(authkey)

            try:
                base64.b64decode(authkey, validate=True)
            except Exception as e:
                raise ValueError("authkey is not a valid base64 encoded string") from e

        self._authkey = authkey

    @property
    def debug(self) -> bool:
        """Whether the debug logs are being shown in stdout"""
        return logging.getLogger("genshin").level == logging.DEBUG

    @debug.setter
    def debug(self, debug: bool) -> None:
        logging.basicConfig()
        level = logging.DEBUG if debug else logging.NOTSET
        logging.getLogger("genshin").setLevel(level)

    def set_cookies(
        self, cookies: Union[Mapping[str, Any], str] = None, **kwargs: Any
    ) -> Mapping[str, str]:
        """Helper cookie setter that accepts cookie headers

        :returns: The new cookies
        """
        if not bool(cookies) ^ bool(kwargs):
            raise TypeError("Cannot use both positional and keyword arguments at once")

        cookies = cookies or kwargs
        cookies = {morsel.key: morsel.value for morsel in SimpleCookie(cookies).values()}
        self.cookies = cookies
        return self.cookies

    def set_browser_cookies(self, browser: str = None) -> Mapping[str, str]:
        """Extract cookies from your browser and set them as client cookies

        Avalible browsers: chrome, chromium, opera, edge, firefox

        :param browser: The browser to extract the cookies from
        :returns: The extracted cookies
        """
        self.cookies = get_browser_cookies(browser)
        return self.cookies

    def set_authkey(self, authkey: str = None) -> None:
        """Sets an authkey for wish & transaction logs

        :param authkey: An authkey, a url containing an authkey or a path towards a logfile
        :returns: The new authkey
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
        """Create and set a new cache for http requests

        :param maxsize: The maximum size of the cache
        :param strategy: The cache strategy to use, defaults to Least-Recently-Used
        :param ttl: The time to live of items, only works with LRU caches
        :param getsizeof: Function that gets the size of any objecct, by default everything has size of 1
        :returns: The newly created cache
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

    async def _check_cache(
        self,
        key: Tuple[Any, ...],
        check: Callable[[Any], bool] = None,
        *,
        lang: str = None,
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

    async def _update_cache(
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

        if check is not None and not check(data):
            return

        self.cache[key] = data

    # ASYNCIO HANDLERS:

    async def close(self) -> None:
        """Close the underlying aiohttp session"""
        if not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        await self.close()

    # RAW HTTP REQUESTS:

    @handle_ratelimits()
    async def request(
        self,
        url: Union[str, URL],
        method: str = "GET",
        *,
        headers: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request and return a parsed json response"""
        asyncio.create_task(self._fetch_mi18n())

        headers = headers or {}
        headers["User-Agent"] = self.USER_AGENT

        async with self.session.request(method, url, headers=headers, **kwargs) as r:
            r.raise_for_status()
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
        url = URL(self.WEBSTATIC_URL).join(URL(url))

        data = get_from_static_cache(str(url))
        if data is not None:
            return data

        headers = headers or {}
        headers["user-agent"] = self.USER_AGENT

        self.logger.debug(f"STATIC {url}")

        async with self.session.get(url, headers=headers, **kwargs) as r:
            r.raise_for_status()
            data = await r.json()

        if cache:
            save_to_static_cache(str(url), data)

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
            data = await self._check_cache(cache, cache_check, lang=lang)
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
            await self._update_cache(data, cache, cache_check, lang=lang)

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

    async def request_ledger(
        self,
        uid: int = None,
        detail: bool = False,
        *,
        month: int = None,
        lang: str = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make a request towards the ys ledger endpoint

        Traveler's diary related data
        """
        params = params or {}

        url = URL(self.DETAIL_LEDGER_URL if detail else self.INFO_LEDGER_URL)

        params.update(await self._complete_uid(uid))
        params["month"] = month or datetime.now().month
        params["lang"] = lang or self.lang

        debug_url = url.with_query(params)
        self.logger.debug(f"DIARY GET {debug_url}")

        return await self.request(url, params=params)

    async def request_calculator(
        self,
        endpoint: str,
        *,
        method: str = "POST",
        lang: str = None,
        params: Dict[str, Any] = None,
        json: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the calculator endpoint

        Calculator database and resource calculation
        """
        params = params or {}
        json = json or {}

        if not self.cookies:
            raise RuntimeError("No cookies provided")

        url = URL(self.CALCULATOR_URL).join(URL(endpoint))

        if method == "GET":
            params["lang"] = lang or self.lang
            json = None
        else:
            json["lang"] = lang or self.lang

        self.logger.debug(f"CALC {method} {url.with_query(params)}")

        return await self.request(url, method, params=params, json=json, **kwargs)

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
        authkey: Optional[str] = None,
        params: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the game info endpoint

        Wish history related data
        """
        params = params or {}
        authkey = authkey or self.authkey

        if authkey is None:
            raise RuntimeError("No authkey provided")

        base_url = URL(self.GACHA_INFO_URL)
        url = base_url.join(URL(endpoint))

        params["authkey_ver"] = 1
        params["authkey"] = unquote(authkey)
        params["lang"] = create_short_lang_code(lang or self.lang)

        debug_url = url.with_query({k: v for k, v in params.items() if k != "authkey"})
        self.logger.debug(f"GACHA {method} {debug_url}")

        return await self.request(url, method, params=params, **kwargs)

    async def request_transaction(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: str = None,
        authkey: Optional[str] = None,
        params: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the transaction log endpoint

        Transaction related data
        """
        params = params or {}
        authkey = authkey or self.authkey

        if authkey is None:
            raise RuntimeError("No authkey provided")

        base_url = URL(self.YSULOG_URL)
        url = base_url.join(URL(endpoint))

        params["authkey_ver"] = 1
        params["sign_type"] = 2
        params["authkey"] = unquote(authkey)
        params["lang"] = create_short_lang_code(lang or self.lang)

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

    async def login_with_ticket(self, login_ticket: str = "") -> None:
        """Complete cookies using a login ticket"""
        url = "https://webapi-os.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket"
        async with self.session.get(url, params=dict(login_ticket=login_ticket)) as r:
            r.raise_for_status()

    # HOYOLAB:

    async def genshin_accounts(self, *, lang: str = None) -> List[GenshinAccount]:
        """Get the genshin accounts of the currently logged-in user

        :params lang: The language to use
        """
        # TODO: Account for honkai accounts

        # fmt: off
        data = await self.request_hoyolab(
            "binding/api/getUserGameRolesByCookie",
            lang=lang,
            cache=("accounts", self.hoyolab_uid)
        )
        # fmt: on
        return [GenshinAccount(**i) for i in data["list"]]

    async def search_users(self, keyword: str, *, lang: str = None) -> List[SearchUser]:
        """Search hoyolab users

        :param keyword: The keyword to search with
        :params lang: The language to use
        """
        data = await self.request_hoyolab(
            "community/search/wapi/search/user",
            lang=lang,
            params=dict(keyword=keyword, page_size=20),
            cache=("search", keyword),
        )
        return [SearchUser(**i["user"]) for i in data["list"]]

    async def set_visibility(self, public: bool) -> None:
        """Sets your data to public or private.

        :param public: Whether the data should now be public
        """
        await self.request_game_record(
            "genshin/wapi/publishGameRecord",
            method="POST",
            json=dict(is_public=public, game_id=2),
        )

    async def get_recommended_users(self, *, limit: int = 200) -> List[SearchUser]:
        """Get a list of recommended active users

        :param limit: The maximum amount of users to return
        """
        data = await self.request_hoyolab(
            "community/user/wapi/recommendActive",
            params=dict(page_size=limit),
        )
        return [SearchUser(**i["user"]) for i in data["list"]]

    async def redeem_code(self, code: str, uid: int = None, *, lang: str = None) -> None:
        """Redeems a gift code for the current user

        :param code: The code to redeem
        :param uid: The specific uid to redeem for
        :param lang: The language to use
        """
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

    async def __fetch_user(self, uid: int, lang: str = None) -> Dict[str, Any]:
        """Low-level http method for fetching the game record index"""
        server = recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/index",
            lang=lang,
            params=dict(server=server, role_id=uid),
            cache=("user", uid),
        )
        return data

    async def __fetch_characters(
        self, uid: int, character_ids: List[int], individual: bool = False, lang: str = None
    ) -> List[Dict[str, Any]]:
        """Low-level http method for fetching the game record characters

        Caching with characters is optimized
        """
        if not character_ids:
            return []

        character_ids = sorted(set(character_ids))

        if individual:
            sem = asyncio.Semaphore(5)

            async def _helper(character_id: int):
                async with sem:
                    c = await self.__fetch_characters(uid, [character_id], lang=lang)
                return c[0]

            data = await asyncio.gather(*map(_helper, character_ids), return_exceptions=True)
            return [i for i in data if not isinstance(i, BaseException)]

        # try to get all the characters from the cache
        coros = [
            asyncio.create_task(self._check_cache(("character", uid, charid), lang=lang))
            for charid in character_ids
        ]
        characters = await asyncio.gather(*coros)
        if all(characters):
            # mypy bug - all does not function as a type guard
            return sorted(characters, key=lambda c: c["id"])  # type: ignore

        server = recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/character",
            method="POST",
            lang=lang,
            json=dict(character_ids=character_ids, role_id=uid, server=server),
        )

        # update the cache one by one
        characters = data["avatars"]
        coros = [
            asyncio.create_task(self._update_cache(char, ("character", uid, char["id"])))
            for char in characters
        ]
        await asyncio.wait(coros)

        return sorted(characters, key=lambda c: c["id"])

    async def get_record_card(self, hoyolab_uid: int = None, *, lang: str = None) -> RecordCard:
        """Get a user's record card

        :param hoyolab_uid: A hoyolab uid
        :param lang: The language to use
        """
        data = await self.request_game_record(
            "card/wapi/getGameRecordCard",
            lang=lang,
            params=dict(uid=hoyolab_uid or self.hoyolab_uid),
            cache=("record", hoyolab_uid),
            cache_check=lambda data: len(data["list"]) > 0,
        )
        cards = data["list"]
        if not cards:
            raise errors.DataNotPublic({"retcode": 10102})

        return RecordCard(**cards[0])

    async def get_user(
        self,
        uid: int,
        *,
        character_ids: List[int] = None,
        all_characters: bool = False,
        lang: str = None,
    ) -> UserStats:
        """Get a user's stats and characters

        :param uid: A Genshin uid
        :param character_ids: The ids of characters you want to fetch
        :param all_characters: Whether to get every single character a user has. Discouraged.
        :param lang: The language to use
        """
        # TODO: Optimize all_characters
        if character_ids is None:
            character_ids = list(CHARACTER_NAMES) if all_characters else []

        data = await self.__fetch_user(uid, lang=lang)
        character_ids = [char["id"] for char in data["avatars"]] + character_ids
        data["avatars"] = await self.__fetch_characters(
            uid,
            character_ids,
            individual=all_characters,
            lang=lang,
        )

        return UserStats(**data)

    async def get_partial_user(self, uid: int, *, lang: str = None) -> PartialUserStats:
        """Helper function to get a user without any equipment

        :param uid: A Genshin uid
        :param lang: The language to use
        """
        data = await self.__fetch_user(uid, lang=lang)
        return PartialUserStats(**data)

    async def get_characters(
        self,
        uid: int,
        character_ids: List[int],
        *,
        individual: bool = False,
        lang: str = None,
    ) -> List[Character]:
        """Helper function to fetch characters from just their ids

        :param uid: A Genshin uid
        :param character_ids: The ids of characters you want to fetch
        :param individual: Whether to get all characters individual in order to return only the ones the user has
        :param lang: The language to use
        """
        data = await self.__fetch_characters(uid, character_ids, individual=individual, lang=lang)
        return [Character(**i) for i in data]

    async def get_spiral_abyss(
        self, uid: int, *, previous: bool = False, lang: str = None
    ) -> SpiralAbyss:
        """Get spiral abyss runs

        :param uid: A Genshin uid
        :param previous: Whether to get the record of the previous spiral abyss
        :param lang: The language to use
        """
        server = recognize_server(uid)
        schedule_type = 2 if previous else 1
        data = await self.request_game_record(
            "genshin/api/spiralAbyss",
            params=dict(role_id=uid, server=server, schedule_type=schedule_type),
            cache=("abyss", uid, schedule_type),
        )
        return SpiralAbyss(**data)

    async def get_notes(self, uid: int, *, lang: str = None) -> Notes:
        """Get the real-time notes.

        :param uid: A Genshin uid
        :param lang: The language to use
        """
        server = recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/dailyNote",
            lang=lang,
            params=dict(server=server, role_id=uid),
        )
        return Notes(**data)

    async def get_activities(self, uid: int, *, lang: str = None) -> Activities:
        """Get activities

        :param uid: A Genshin uid
        :param lang: The language to use
        """
        server = recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/activities",
            lang=lang,
            params=dict(server=server, role_id=uid),
            cache=("activities", uid),
        )
        return Activities(**data)

    async def get_full_user(self, uid: int, *, lang: str = None) -> FullUserStats:
        """Get a user with all their possible data

        :param uid: A Genshin uid
        :param lang: The language to use
        """
        user, abyss1, abyss2, activities = await asyncio.gather(
            self.get_user(uid, lang=lang),
            self.get_spiral_abyss(uid, previous=False),
            self.get_spiral_abyss(uid, previous=True),
            self.get_activities(uid, lang=lang),
        )
        abyss = {"current": abyss1, "previous": abyss2}
        return FullUserStats(**user.dict(), abyss=abyss, activities=activities)

    # LEDGER:

    async def get_diary(self, uid: int = None, *, month: int = None, lang: str = None) -> Diary:
        """Get a traveler's diary with earning details for the month

        :param uid: Genshin uid of the currently logged-in user
        :param month: The month in the year to see the history for
        :param lang: The language to use
        """
        data = await self.request_ledger(uid, month=month, lang=lang)
        return Diary(**data)

    def diary_log(
        self,
        uid: int = None,
        *,
        mora: bool = False,
        month: int = None,
        limit: int = None,
        lang: str = None,
    ) -> DiaryPaginator:
        """Create a new daily reward pagintor

        :param client: A client for making http requests
        :param uid: Genshin uid of the currently logged-in user
        :param mora: Whether the type of currency should be mora instead of primogems
        :param month: The month in the year to see the history for
        :param limit: The maximum amount of actions to get
        :param lang: The language to use
        """
        type = 2 if mora else 1
        return DiaryPaginator(self, uid, type, month, limit, lang)

    # CALCULATOR

    async def calculate(
        self,
        character: Union[Tuple[int, int, int], Tuple[int, int, int, int]] = None,
        weapon: Tuple[int, int, int] = None,
        artifacts: Union[Sequence[Tuple[int, int, int]], Mapping[int, Tuple[int, int]]] = None,
        talents: Union[Sequence[Tuple[int, int, int]], Mapping[int, Tuple[int, int]]] = None,
        *,
        lang: str = None,
    ):
        json: Dict[str, Any] = {}

        if character:
            if len(character) == 4:
                # highly problematic section for mypy, we have to be very explicit
                cid, json["element_attr_id"], cl, tl = cast(Tuple[int, int, int, int], character)
                character = (cid, cl, tl)

            json.update(CalculatorObject(*character)._serialize(prefix="avatar_"))
            if character[0] in (10000005, 10000007):
                raise ValueError("No element provided for the traveler")

        if talents:
            if isinstance(talents, Mapping):
                talents = [(k, *v) for k, v in talents.items()]
            json["skill_list"] = [CalculatorObject(*i)._serialize() for i in talents]

        if weapon:
            json["weapon"] = CalculatorObject(*weapon)._serialize()

        if artifacts:
            if isinstance(artifacts, Mapping):
                artifacts = [(k, *v) for k, v in artifacts.items()]
            json["reliquary_list"] = [CalculatorObject(*i)._serialize() for i in artifacts]

        data = await self.request_calculator("compute", lang=lang, json=json)
        return CalculatorResult(**data)

    async def _get_calculator_items(
        self,
        slug: str,
        filters: Dict[str, Any],
        query: str = None,
        *,
        lang: str = None,
    ) -> List[Dict[str, Any]]:
        """Get all items of a specific slug from a calculator"""
        if query and any(isinstance(v, list) and v for v in filters.values()):
            raise TypeError("Cannot specify a query and filter at the same time")

        data = await self.request_calculator(
            f"{slug}/list",
            lang=lang,
            json=dict(
                page=1,
                size=69420,
                keywords=query,
                **filters,
            ),
        )
        return data["list"]

    async def get_calculator_characters(
        self,
        *,
        query: str = None,
        elements: Sequence[int] = None,
        weapon_types: Sequence[int] = None,
        lang: str = None,
    ) -> List[CalculatorCharacter]:
        """Get all characters provided by the Enhancement Progression Calculator

        :param query: A query to use when searching; incompatible with other filters
        :param elements: The elements of returned characters - refer to `.models.CALCULATOR_ELEMENTS`
        :param weapon_types: The weapon types of returned characters - refer to `.models.CALCULATOR_WEAPON_TYPES`
        :param lang: The language to use
        """
        data = await self._get_calculator_items(
            "avatar",
            lang=lang,
            query=query,
            filters=dict(
                element_attr_ids=elements or [],
                weapon_cat_ids=weapon_types or [],
            ),
        )
        return [CalculatorCharacter(**i) for i in data]

    async def get_calculator_weapons(
        self,
        *,
        query: str = None,
        types: Sequence[int] = None,
        rarities: Sequence[int] = None,
        lang: str = None,
    ) -> List[CalculatorWeapon]:
        """Get all weapons provided by the Enhancement Progression Calculator

        :param query: A query to use when searching; incompatible with other filters
        :param types: The types of returned weapons - refer to `.models.CALCULATOR_WEAPON_TYPES`
        :param rarities: The rarities of returned weapons
        :param lang: The language to use
        """
        data = await self._get_calculator_items(
            "weapon",
            lang=lang,
            query=query,
            filters=dict(
                weapon_cat_ids=types or [],
                weapon_levels=rarities or [],
            ),
        )
        return [CalculatorWeapon(**i) for i in data]

    async def get_calculator_artifacts(
        self,
        *,
        query: str = None,
        pos: int = 1,
        rarities: Sequence[int] = None,
        lang: str = None,
    ) -> List[CalculatorArtifact]:
        """Get all artifacts provided by the Enhancement Progression Calculator

        :param query: A query to use when searching; incompatible with other filters
        :param pos: The slot position of the returned weapon
        :param rarities: The rarities of returned artifacts
        :param lang: The language to use
        """
        data = await self._get_calculator_items(
            "reliquary",
            lang=lang,
            query=query,
            filters=dict(
                reliquary_cat_id=pos,
                reliquary_levels=rarities or [],
            ),
        )
        return [CalculatorArtifact(**i) for i in data]

    async def get_character_talents(
        self,
        character_id: int,
        *,
        lang: str = None,
    ) -> List[CalculatorTalent]:
        """Get the talents of a character

        :param lang: The language to use
        """
        data = await self.request_calculator(
            "avatar/skill_list",
            method="GET",
            lang=lang,
            params=dict(avatar_id=character_id),
        )
        return [CalculatorTalent(**i) for i in data["list"]]

    async def get_complete_artifact_set(
        self,
        artifact_id: int,
        *,
        lang: str = None,
    ) -> List[CalculatorArtifact]:
        """Get all other artifacts that share a set with any given artifact

        :param lang: The language to use
        """
        data = await self.request_calculator(
            "reliquary/set",
            method="GET",
            lang=lang,
            params=dict(reliquary_id=artifact_id),
        )
        return [CalculatorArtifact(**i) for i in data["reliquary_list"]]

    # DAILY REWARDS:

    async def get_reward_info(self, *, lang: str = None) -> DailyRewardInfo:
        """Get the daily reward info for the current user

        :param lang: The language to use
        """
        data = await self.request_daily_reward("info", lang=lang)
        return DailyRewardInfo(data["is_sign"], data["total_sign_day"])

    async def get_monthly_rewards(self, *, lang: str = None) -> List[DailyReward]:
        """Get a list of all availible rewards for the current month

        :param lang: The language to use
        """
        func = perm_cache(
            ("rewards", datetime.utcnow().month, lang or self.lang),
            self.request_daily_reward,
        )
        data = await func("home", lang=lang)
        return [DailyReward(**i) for i in data["awards"]]

    def claimed_rewards(self, *, limit: int = None, lang: str = None) -> DailyRewardPaginator:
        """Get all claimed rewards for the current user

        NOTE: Languages are currently broken,
        the language is based off the language used to claim the reward

        :param limit: The maximum amount of rewards to get
        :param lang: The language to use - currently broken
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

        :param lang: The language to use
        :param reward: Whether to also fetch the claimed reward
        """
        await self.request_daily_reward("sign", method="POST", lang=lang)

        if not reward:
            return None

        info, rewards = await asyncio.gather(
            self.get_reward_info(lang=lang),
            self.get_monthly_rewards(lang=lang),
        )
        return rewards[info.claimed_rewards - 1]

    # WISH HISTORY:

    @overload
    def wish_history(
        self,
        banner_type: Optional[List[BannerType]] = ...,
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
        banner_type: BannerType,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> WishHistory:
        ...

    def wish_history(
        self,
        banner_type: Union[BannerType, List[BannerType]] = None,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> Union[WishHistory, MergedWishHistory]:
        """Get the wish history of a user

        :param banner_type: The banner(s) from which to get the wishes
        :param limit: The maximum amount of wishes to get
        :param lang: The language to use
        :param authkey: The authkey to use when requesting data
        :param end_id: The ending id to start getting data from
        """
        cls = WishHistory if isinstance(banner_type, int) else MergedWishHistory
        return cls(
            self,
            banner_type,  # type: ignore
            lang=lang,
            authkey=authkey,
            limit=limit,
            end_id=end_id,
        )

    async def get_banner_names(
        self, *, lang: str = None, authkey: str = None
    ) -> Dict[BannerType, str]:
        """Get a list of banner names

        :param lang: The language to use
        :param authkey: The authkey to use when requesting data
        """
        func = perm_cache(("banners", lang or self.lang), self.request_gacha_info)
        data = await func(
            "getConfigList",
            lang=lang,
            authkey=authkey,
        )
        return {int(i["key"]): i["name"] for i in data["gacha_type_list"]}  # type: ignore

    async def _get_banner_details(self, banner_id: str, *, lang: str = None) -> BannerDetails:
        """Get details of a specific banner using its id

        :param banner_id: A banner id
        :param lang: The language to use
        """
        data = await self.request_webstatic(
            f"/hk4e/gacha_info/os_asia/{banner_id}/{lang or self.lang}.json"
        )
        return BannerDetails(**data)

    async def get_banner_details(
        self, banner_ids: List[str] = None, *, lang: str = None
    ) -> List[BannerDetails]:
        """Get all banner details at once in a batch

        :param banner_ids: A list of banner ids, implicitly fetched when not provided
        :param lang: The language to use
        """
        try:
            banner_ids = banner_ids or get_banner_ids()
        except FileNotFoundError:
            banner_ids = []

        if len(banner_ids) < 3:
            banner_ids = await self.fetch_banner_ids()

        data = await asyncio.gather(*(self._get_banner_details(i, lang=lang) for i in banner_ids))
        return list(data)

    async def get_gacha_items(
        self, *, server: str = "os_asia", lang: str = None
    ) -> List[GachaItem]:
        """Get the list of characters and weapons that can be gotten from the gacha.

        :param server: The server to request the items from
        :param lang: The language to use
        """
        data = await self.request_webstatic(
            f"/hk4e/gacha_info/{server}/items/{lang or self.lang}.json", cache=False
        )
        return [GachaItem(**i) for i in data]

    # TRANSACTIONS:

    async def _get_transaction_reasons(self, lang: str) -> Dict[str, str]:
        """Get a mapping of transaction reasons

        :param lang: The language to use
        """
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
        kind: Optional[List[TransactionKind]] = ...,
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
        kind: Union[TransactionKind, List[TransactionKind]] = None,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> Union[Transactions[Any], MergedTransactions]:
        """Get the transaction log of a user

        :param kind: The kind(s) of transactions to get
        :param limit: The maximum amount of wishes to get
        :param lang: The language to use
        :param authkey: The authkey to use when requesting data
        :param end_id: The ending id to start getting data from
        """
        cls = Transactions if isinstance(kind, str) else MergedTransactions
        return cls(
            self,
            kind,  # type: ignore
            lang=lang,
            authkey=authkey,
            limit=limit,
            end_id=end_id,
        )

    # INTERACTIVE MAP:

    async def _get_map_pin_icons(self, map_id: int = 2, *, lang: str = None) -> Dict[int, str]:
        """Get the icons of pins"""
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
        """Get the map tree of all categories & lables of map points

        :param map_id: The id of the map
        :param lang: The language to use
        """
        data = await self.request_map("map/label/tree", lang=lang, map_id=map_id, static=True)
        return [MapNode(**i) for i in data["tree"]]

    async def get_map_points(
        self, map_id: int = 2, *, lang: str = None
    ) -> Tuple[List[MapNode], List[MapPoint]]:
        """Get a tuple of all map lables and map points

        :param map_id: The id of the map
        :param lang: The language to use
        """
        data = await self.request_map("map/point/list", lang=lang, map_id=map_id, static=True)

        labels = [MapNode(**i) for i in data["label_list"]]
        points = [MapPoint(**i) for i in data["point_list"]]

        return labels, points

    async def get_map_locations(self, map_id: int = 2, *, lang: str = None) -> List[MapLocation]:
        """Get a list of all locations on a map

        :param map_id: The id of the map
        :param lang: The language to use
        """
        data = await self.request_map("map/map_anchor/list", lang=lang, map_id=map_id, static=True)

        return [MapLocation(**i) for i in data["list"]]

    # MISC:

    async def _complete_uid(
        self,
        uid: Optional[int] = None,
        uid_key: str = "uid",
        server_key: str = "region",
    ) -> Dict[str, Any]:
        """Create a new dict with a uid and a server

        These are fetched from the currently authenticated user
        """
        params: Dict[str, Any] = {}

        uid = uid or self._uid

        if uid is None:
            accounts = await self.genshin_accounts()
            # filter test servers
            accounts = [
                account for account in accounts if "os" in account.server or "cn" in account.server
            ]

            # TODO: Raise properly
            if not accounts:
                errors.raise_for_retcode({"retcode": -1073})

            account = max(accounts, key=lambda a: a.level)
            uid = account.uid

            self._uid = uid

        params[uid_key] = uid
        params[server_key] = recognize_server(uid)

        return params

    async def _fetch_mi18n(self) -> Dict[str, Dict[str, str]]:
        if self.fetched_mi18n:
            return GenshinModel._mi18n

        self.fetched_mi18n = True

        async def single(url: str, key: str, lang: str = None):
            if lang is None:
                coros = (single(url, key, l) for l in LANGS)
                return await asyncio.gather(*coros)

            data = await self.request_webstatic(url.format(lang=lang))
            for k, v in data.items():
                GenshinModel._mi18n.setdefault(key + "/" + k, {})[lang] = v

        coros = (single(url, key) for key, url in GenshinModel._mi18n_urls.items())
        await asyncio.gather(*coros)

        return GenshinModel._mi18n

    async def init(self, lang: str = None):
        """Request all static & permanent endpoints to not require them later

        :param lang: The language to use
        """
        lang = lang or self.lang

        await asyncio.gather(
            self.get_banner_names(lang=lang),
            self.get_banner_details(lang=lang),
            self.get_monthly_rewards(),
            self._get_transaction_reasons(lang=lang),
            self._fetch_mi18n(),
        )

    async def fetch_banner_ids(self) -> List[str]:
        """Fetch banner ids from a user-mantained repo"""
        url = "https://raw.githubusercontent.com/thesadru/genshindata/master/banner_ids.txt"
        async with self.session.get(url) as r:
            data = await r.text()
        return data.splitlines()


class ChineseClient(GenshinClient):
    """A Genshin Client for chinese endpoints"""

    DS_SALT = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
    SIGNIN_SALT = "4a8knnbk5pbjqsrudp3dq484m9axoc5g"
    ACT_ID = "e202009291139501"

    TAKUMI_URL = "https://api-takumi.mihoyo.com/"
    RECORD_URL = "https://api-takumi.mihoyo.com/game_record/app/"
    INFO_LEDGER_URL = "https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo"
    DETAIL_LEDGER_URL = "https://hk4e-api.mihoyo.com/event/ys_ledger/monthDetail"
    REWARD_URL = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/"
    GACHA_INFO_URL = "https://hk4e-api.mihoyo.com/event/gacha_info/api/"
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
        json: Any = None,
        params: Dict[str, Any] = None,
        cache: Tuple[Any, ...] = None,
        cache_check: Callable[[Any], bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        kwargs.pop("lang", None)
        params = params or {}

        if cache:
            data = await self._check_cache(cache, cache_check)
            if data:
                return data

        if not self.cookies:
            raise RuntimeError("No cookies provided")

        url = URL(self.TAKUMI_URL).join(URL(endpoint))

        # all of this repetition is literally just to change these few lines
        headers = {
            "x-rpc-app_version": "2.11.1",
            "x-rpc-client_type": "5",
            "ds": generate_cn_dynamic_secret(self.DS_SALT, json, params),
        }

        debug_url = url.with_query(params)
        self.logger.debug(f"RECORD {method} {debug_url}")

        data = await self.request(url, method, headers=headers, json=json, params=params, **kwargs)

        if cache:
            await self._update_cache(data, cache, cache_check)

        return data

    async def request_ledger(
        self,
        uid: int = None,
        detail: bool = False,
        *,
        month: int = None,
        params: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the ys ledger endpoint

        Traveler's diary related data
        """
        kwargs.pop("lang", None)
        params = params or {}

        url = URL(self.DETAIL_LEDGER_URL if detail else self.INFO_LEDGER_URL)

        params.update(await self._complete_uid(uid, "bind_uid", "bind_region"))
        params["month"] = month or datetime.now().month

        debug_url = url.with_query(params)
        self.logger.debug(f"DIARY GET {debug_url}")

        return await self.request(url, params=params)

    async def request_daily_reward(
        self,
        endpoint: str,
        uid: int = None,
        *,
        method: str = "GET",
        params: Dict[str, Any] = None,
        headers: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        kwargs.pop("lang", None)
        headers = headers or {}
        params = params or {}

        if not self.cookies:
            raise RuntimeError("No cookies provided")

        url = URL(self.REWARD_URL).join(URL(endpoint))

        params.update(await self._complete_uid(uid))

        headers["x-rpc-app_version"] = "2.10.1"
        headers["x-rpc-client_type"] = "5"
        headers["x-rpc-device_id"] = str(uuid.uuid4())
        headers["ds"] = generate_dynamic_secret(self.SIGNIN_SALT)

        params["act_id"] = self.ACT_ID

        self.logger.debug(f"DAILY {method} {url.with_query(params)}")

        return await self.request(url, method, params=params, headers=headers, **kwargs)

    async def get_reward_info(self, uid: int = None) -> DailyRewardInfo:
        """Get the daily reward info for the current user

        :param uid: Genshin uid of the currently logged-in user
        """
        data = await self.request_daily_reward("info", uid)
        return DailyRewardInfo(data["is_sign"], data["total_sign_day"])

    async def get_monthly_rewards(self) -> List[DailyReward]:
        """Get a list of all availible rewards for the current month"""
        # uid doesn't matter, this is a static resource
        func = perm_cache(
            ("cn_rewards", datetime.utcnow().month),
            self.request_daily_reward,
        )
        data = await func("home", uid=1)
        return [DailyReward(**i) for i in data["awards"]]

    def claimed_rewards(self, uid: int = None, *, limit: int = None) -> ChineseDailyRewardPaginator:
        """Get all claimed rewards for the current user

        NOTE: Languages are currently broken,
        the language is based off the language used to claim the reward

        :param limit: The maximum amount of rewards to get
        :param lang: The language to use - currently broken
        """
        return ChineseDailyRewardPaginator(self, uid, limit=limit)

    @overload
    async def claim_daily_reward(
        self, uid: int = None, *, reward: Literal[True] = ...
    ) -> DailyReward:
        ...

    @overload
    async def claim_daily_reward(self, uid: int = None, *, reward: Literal[False]) -> None:
        ...

    async def claim_daily_reward(
        self, uid: int = None, *, reward: bool = True
    ) -> Optional[DailyReward]:
        """Signs into hoyolab and claims the daily reward.

        :param uid: Genshin uid of the currently logged-in user
        :param reward: Whether to also fetch the claimed reward
        """
        await self.request_daily_reward("sign", uid, method="POST")

        if not reward:
            return None

        info, rewards = await asyncio.gather(
            self.get_reward_info(),
            self.get_monthly_rewards(),
        )
        return rewards[info.claimed_rewards - 1]


class MultiCookieClient(GenshinClient):
    """A Genshin Client which allows setting multiple cookies"""

    sessions: List[aiohttp.ClientSession]

    def __init__(
        self,
        cookie_list: Iterable[Mapping[str, str]] = None,
        *,
        lang: str = "en-us",
        debug: bool = False,
    ) -> None:
        self.sessions = []

        if cookie_list:
            self.set_cookies(cookie_list)

        super().__init__(lang=lang, debug=debug)

    @property
    def session(self) -> aiohttp.ClientSession:
        """The currently chosen session"""
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
        self,
        cookie_list: Union[Iterable[Union[Mapping[str, Any], str]], str],
        clear: bool = True,
    ) -> List[Mapping[str, str]]:
        """Set a list of cookies

        :param cookie_list: A list of cookies or a json file containing cookies
        :param clear: Whether to clear all of the previous cookies
        """
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

        return self.cookies

    def set_browser_cookies(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise RuntimeError(f"{type(self).__name__} does not support browser cookies")

    async def close(self) -> None:
        """Close the underlying aiohttp sessions"""
        tasks = [
            asyncio.create_task(session.close()) for session in self.sessions if not session.closed
        ]
        if tasks:
            await asyncio.wait(tasks)

        await super().close()

    async def request(
        self,
        url: Union[str, URL],
        method: str = "GET",
        headers: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        headers = headers or {}
        headers["user-agent"] = self.USER_AGENT

        for session in self.sessions.copy():
            async with session.request(method, url, headers=headers, **kwargs) as r:
                r.raise_for_status()
                data = await r.json()

            if data["retcode"] == 0:
                return data["data"]

            try:
                errors.raise_for_retcode(data)
            except errors.TooManyRequests:
                # move the ratelimited session to the end to let the ratelimit wear off
                session = self.sessions.pop(0)
                self.sessions.append(session)

        # if we're here it means we used up all our sessions so we must handle that
        msg = "All cookies have hit their request limit of 30 accounts per day."
        raise errors.TooManyRequests({"retcode": 10101}, msg)

    async def request_daily_reward(self, *args: Any, **kwargs: Any) -> NoReturn:
        """Helper overwrite to prevent nasty bugs"""
        raise RuntimeError(f"{type(self).__name__} does not support daily reward endpoints")


class ChineseMultiCookieClient(MultiCookieClient, ChineseClient):
    """A Genshin Client for chinese endpoints which allows setting multiple cookies"""


class InternationalClient:
    """A client dummy which accepts both overseas and chinese cookies

    Currently in development and probably shouldn't be used.
    """

    os_client: MultiCookieClient
    cn_client: ChineseMultiCookieClient

    def __init__(
        self,
        os_client: MultiCookieClient = None,
        cn_client: ChineseMultiCookieClient = None,
        *,
        debug: bool = False,
    ) -> None:
        warnings.warn("Initialized an unstable InteractionClient type")

        self.os_client = os_client or MultiCookieClient(debug=debug)
        self.cn_client = cn_client or ChineseMultiCookieClient(debug=debug)

    async def close(self):
        await asyncio.gather(self.os_client.close(), self.cn_client.close())

    async def set_cookies(
        self,
        cookies: Sequence[Mapping[str, Any]] = None,
        *,
        os: Sequence[Mapping[str, Any]] = None,
        cn: Sequence[Mapping[str, Any]] = None,
    ) -> Tuple[List[Mapping[str, Any]], List[Mapping[str, Any]]]:
        """Helper cookie setter that accepts cookie headers

        It is recommended to set os and cn cookies explicitly.

        :param cookies: A list of either os or cn cookies if unknown
        :param os: A list of cookies known to be os
        :param cn: A list of cookies known to be cn
        :returns: A tuple of os cookies and cn cookies
        """
        cookies = cookies or []
        os = os or []
        cn = cn or []

        async def is_chinese(cookies: Mapping[str, Any]) -> bool:
            os = GenshinClient(cookies)
            cn = ChineseClient(cookies)

            osd, cnd = await asyncio.gather(
                os.request_hoyolab(f"community/user/wapi/getUserFullInfo?uid={os.hoyolab_uid}"),
                cn.request_hoyolab(f"user/wapi/getUserFullInfo?uid={os.hoyolab_uid}"),
                return_exceptions=True,
            )
            await asyncio.gather(os.close(), cn.close())

            if not isinstance(cnd, Exception):
                return True
            elif not isinstance(osd, Exception):
                return False

            raise Exception(f"Cookie {cookie!r} can't be found on neither os nor cn servers")

        self.os_client.set_cookies(os, clear=False)
        self.cn_client.set_cookies(cn, clear=False)

        are_chinese = await asyncio.gather(*(is_chinese(i) for i in cookies))
        for cookie, chinese in zip(cookies, are_chinese):
            if chinese:
                self.cn_client.set_cookies([cookie], clear=False)
            else:
                self.os_client.set_cookies([cookie], clear=False)

        return self.os_client.cookies, self.cn_client.cookies

    def get_activities(self, uid: int, *args: Any, **kwargs: Any):
        client = self.cn_client if is_chinese(uid) else self.os_client
        return client.get_activities(uid, *args, **kwargs)

    def get_characters(self, uid: int, *args: Any, **kwargs: Any):
        client = self.cn_client if is_chinese(uid) else self.os_client
        return client.get_characters(uid, *args, **kwargs)

    def get_full_user(self, uid: int, *args: Any, **kwargs: Any):
        client = self.cn_client if is_chinese(uid) else self.os_client
        return client.get_full_user(uid, *args, **kwargs)

    def get_partial_user(self, uid: int, *args: Any, **kwargs: Any):
        client = self.cn_client if is_chinese(uid) else self.os_client
        return client.get_partial_user(uid, *args, **kwargs)

    def get_spiral_abyss(self, uid: int, *args: Any, **kwargs: Any):
        client = self.cn_client if is_chinese(uid) else self.os_client
        return client.get_spiral_abyss(uid, *args, **kwargs)

    def get_user(self, uid: int, *args: Any, **kwargs: Any):
        client = self.cn_client if is_chinese(uid) else self.os_client
        return client.get_user(uid, *args, **kwargs)

    async def get_record_card(self, hoyolab_uid: int, *args: Any, **kwargs: Any):
        try:
            return await self.os_client.get_record_card(hoyolab_uid, *args, **kwargs)
        except:
            return await self.cn_client.get_record_card(hoyolab_uid, *args, **kwargs)
