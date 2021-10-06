from http.cookies import SimpleCookie
from typing import *

import aiohttp
from yarl import URL

from . import utils
from .constants import LANGS
from .models import *
from .paginator import MergedTransactions, MergedWishHistory, Transactions, WishHistory


class GenshinClient:
    """A simple http client for genshin endpoints"""

    OS_DS_SALT: ClassVar[str] = "6cqshh5dhw73bzxn20oexa9k516chk7s"
    CN_DS_SALT: ClassVar[str] = "14bmu1mz0yuljprsfgpvjh3ju2ni468r"

    WEBSTATIC_URL = "https://webstatic-sea.mihoyo.com/"
    OS_RECORD_URL = "https://api-os-takumi.mihoyo.com/"
    CN_RECORD_URL = "https://api-takumi.mihoyo.com/"
    GACHA_INFO_URL = "https://hk4e-api-os.mihoyo.com/event/gacha_info/api/"
    YSULOG_URL = "https://hk4e-api-os.mihoyo.com/ysulog/api/"

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    _session: Optional[aiohttp.ClientSession] = None

    def __init__(
        self, cookies: Mapping[str, str] = None, lang: str = "en-us", authkey: str = None
    ) -> None:
        self.cookies = cookies or {}
        self.authkey = authkey
        assert lang in LANGS, "Invalid language, must be one of: " + ", ".join(LANGS)
        self.lang = lang

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

    def set_cookies(self, cookies: Union[Mapping[str, Any], str]) -> Mapping[str, str]:
        """Helper cookie setter that accepts cookie headers"""
        cookies = SimpleCookie(cookies)
        self.cookies = cookies
        return {morsel.key: morsel.value for morsel in cookies.values()}

    def set_browser_cookies(self, browser: str = None) -> Mapping[str, str]:
        """Extract cookies from your browser and set them as client cookies

        Refer to get_browser_cookies for more info.
        """
        self.cookies = utils.get_browser_cookies(browser)
        return self.cookies

    @property
    def hoyolab_uid(self) -> Optional[int]:
        """The logged-in user's hoyolab uid"""
        for cookie in self.session.cookie_jar:
            if cookie.key in ("ltuid", "account_id"):
                return int(cookie.value)

        return None

    async def close(self) -> None:
        """Close the client's session"""
        if not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        # create the session
        session = self.session
        return self

    async def __aexit__(self, *exc_info):
        await self.close()

    # RAW HTTP REQUESTS:

    async def request(
        self,
        url: Union[str, URL],
        method: str = "GET",
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

        raise Exception(f"{data['retcode']} - {data['message']}")

    async def request_webstatic(
        self, url: Union[str, URL], headers: Dict[str, Any] = None, **kwargs: Any
    ) -> Any:
        """Request a static json file"""
        headers = headers or {}
        headers["user-agent"] = self.USER_AGENT

        url = URL(self.WEBSTATIC_URL).join(URL(url))

        async with self.session.get(url, headers=headers, **kwargs) as r:
            return await r.json()

    async def request_game_record(
        self,
        endpoint: str,
        method: str = "GET",
        chinese: bool = False,
        lang: str = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the game record endpoint

        User stats related data
        """
        if self.cookies is None:
            raise Exception("No cookies provided")

        base_url = URL(self.CN_RECORD_URL if chinese else self.OS_RECORD_URL)
        url = base_url.join(URL(endpoint))

        headers = {
            "x-rpc-app_version": "2.7.0" if chinese else "1.5.0",
            "x-rpc-client_type": "5" if chinese else "4",
            "x-rpc-language": lang or self.lang,
            "ds": utils.generate_ds_token(self.CN_DS_SALT if chinese else self.OS_DS_SALT),
        }

        return await self.request(url, method, headers=headers, **kwargs)

    async def request_gacha_info(
        self,
        endpoint: str,
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
        params["lang"] = utils.get_short_lang_code(lang or self.lang)

        if authkey is None and self.authkey is None:
            raise Exception("No authkey provided")

        return await self.request(url, method, params=params, **kwargs)

    async def request_transaction(
        self,
        endpoint: str,
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
        params["lang"] = utils.get_short_lang_code(lang or self.lang)

        if authkey is None and self.authkey is None:
            raise Exception("No authkey provided")

        return await self.request(url, method, params=params, **kwargs)

    # HOYOLAB:

    async def accounts(self, *, lang: str = None) -> List[GenshinAccount]:
        """Get the genshin accounts of the currently logged-in user"""
        data = await self.request_game_record("binding/api/getUserGameRolesByCookie", lang=lang)
        return [GenshinAccount(**i) for i in data["list"]]

    async def search_users(self, keyword: str, *, lang: str = None) -> List[SearchUser]:
        data = await self.request_game_record(
            "community/apihub/wapi/search", lang=lang, params=dict(keyword=keyword, size=20, gids=2)
        )
        return [SearchUser(**i) for i in data["users"]]

    # GAME RECORD:

    async def get_record_card(self, hoyolab_uid: int = None, *, lang: str = None) -> RecordCard:
        """Get a user's record card. If a uid is not provided gets the logged in user's"""
        data = await self.request_game_record(
            "game_record/card/wapi/getGameRecordCard",
            lang=lang,
            params=dict(uid=hoyolab_uid or self.hoyolab_uid, gids=2),
        )
        cards = data["list"]
        if not cards:
            raise Exception("User's data is not public")

        return RecordCard(**cards[0])

    async def get_user(self, uid: int, *, lang: str = None) -> PartialUserStats:
        """Get a user's stats and characters"""
        server = utils.recognize_server(uid)
        data = await self.request_game_record(
            "game_record/genshin/api/index", params=dict(server=server, role_id=uid), lang=lang
        )

        character_ids = [char["id"] for char in data["avatars"]]
        character_data = await self.request_game_record(
            "game_record/genshin/api/character",
            method="POST",
            lang=lang,
            json=dict(character_ids=character_ids, role_id=uid, server=server),
        )
        data.update(character_data)

        return UserStats(**data)

    async def get_partial_user(self, uid: int, *, lang: str = None) -> PartialUserStats:
        """Helper alternative function to get a user without any equipment"""
        # return await self.get_user(uid, lang=lang, equipment=False)
        server = utils.recognize_server(uid)
        data = await self.request_game_record(
            "game_record/genshin/api/index", params=dict(server=server, role_id=uid), lang=lang
        )
        return PartialUserStats(**data)

    async def get_spiral_abyss(self, uid: int, *, previous: bool = False) -> SpiralAbyss:
        """Get spiral abyss runs"""
        server = utils.recognize_server(uid)
        schedule_type = 2 if previous else 1
        data = await self.request_game_record(
            "game_record/genshin/api/spiralAbyss",
            params=dict(server=server, role_id=uid, schedule_type=schedule_type),
        )
        return SpiralAbyss(**data)

    async def set_visibility(self, public: bool) -> None:
        """Sets your data to public or private."""
        await self.request_game_record(
            "game_record/genshin/wapi/publishGameRecord",
            method="POST",
            json=dict(is_public=public, game_id=2),
        )

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
                self, banner_type, lang=lang, authkey=authkey, limit=limit, end_id=end_id
            )

    @utils.permanent_cache("lang")
    async def get_banner_types(self, *, lang: str = None, authkey: str = None) -> Dict[int, str]:
        """Get a list of banner types"""
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

    # TRANSACTIONS:

    @utils.permanent_cache("lang")
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
        if kind is None:
            return MergedTransactions(self, lang=lang, authkey=authkey, limit=limit, end_id=end_id)
        else:
            return Transactions(self, kind, lang=lang, authkey=authkey, limit=limit, end_id=end_id)
