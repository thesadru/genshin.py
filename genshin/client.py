from http.cookies import SimpleCookie
from typing import Any, ClassVar, Dict, Literal, Optional, Union, overload

import aiohttp
from yarl import URL

from . import utils
from .models import *
from .paginator import MergedWishHistory, WishHistory


class GenshinClient:
    """A simple http client for genshin endpoints"""

    OS_DS_SALT: ClassVar[str] = "6cqshh5dhw73bzxn20oexa9k516chk7s"
    CN_DS_SALT: ClassVar[str] = "14bmu1mz0yuljprsfgpvjh3ju2ni468r"

    # bbs-api is an alternative
    OS_BBS_URL = "https://bbs-api-os.hoyolab.com/game_record/genshin/api/"
    CN_TAKUMI_URL = "https://api-takumi.mihoyo.com/game_record/genshin/api/"
    GACHA_INFO_URL = "https://hk4e-api-os.mihoyo.com/event/gacha_info/api/"

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    _session: Optional[aiohttp.ClientSession] = None

    def __init__(self, cookies: Dict[str, str] = None, lang: str = "en-us", authkey: str = None) -> None:
        self.cookies = cookies or {}
        self.authkey = authkey
        self.lang = lang

    @property
    def session(self) -> aiohttp.ClientSession:
        """The current client session, created when needed"""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        return self._session

    @property
    def cookies(self) -> Dict[str, str]:
        """The cookie jar belonging to the current session"""
        return {cookie.key: cookie.value for cookie in self.session.cookie_jar}

    @cookies.setter
    def cookies(self, cookies: Dict[str, Any]) -> None:
        cks = {str(key): value for key, value in cookies.items()}
        self.session.cookie_jar.clear()
        self.session.cookie_jar.update_cookies(cks)
    
    def set_cookies(self, cookies: Union[Dict[str, Any], str]) -> Dict[str, str]:
        """Helper cookie setter that accepts cookie headers"""
        cookies = SimpleCookie(cookies)
        self.cookies = cookies
        return {morsel.key: morsel.value for morsel in cookies.values()}
    
    def set_browser_cookies(self, browser: str = None) -> Dict[str, str]:
        """Extract cookies from your browser and set them as client cookies
        
        Refer to get_browser_cookies for more info.
        """
        self.cookies = utils.get_browser_cookies(browser)
        return self.cookies

    @property
    def hoyolab_uid(self) -> Optional[int]:
        """The logged-in user's hoyolab uid"""
        for cookie in self.session.cookie_jar:
            if cookie.key == "ltuid":
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

    async def request_game_record(
        self, endpoint: str, method: str = "GET", chinese: bool = False, lang: str = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Make a request towards the game record endpoint

        User stats related data
        """
        if self.cookies is None:
            raise Exception("No cookies provided")

        base_url = URL(self.CN_TAKUMI_URL if chinese else self.OS_BBS_URL)
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

    # GAME RECORD:
    
    async def get_record_card(self, hoyolab_uid: int = None, *, lang: str = None) -> RecordCard:
        """Get a user's record card. If a uid is not provided gets the logged in user's"""
        data = await self.request_game_record(
            "../../card/wapi/getGameRecordCard",
            lang=lang,
            params=dict(uid=hoyolab_uid or self.hoyolab_uid, gids=2),
        )
        cards = data['list']
        if not cards:
            raise Exception("User's data is not public")
        
        return RecordCard(**cards[0])

    @overload
    async def get_user(self, uid: int, *, lang: str = None, equipment: Literal[True] = ...) -> PartialUserStats:
        ...

    @overload
    async def get_user(self, uid: int, *, lang: str = None, equipment: Literal[False]) -> UserStats:
        ...

    async def get_user(self, uid: int, *, lang: str = None, equipment: bool = True) -> PartialUserStats:
        """Get a user's stats and characters"""
        server = utils.recognize_server(uid)
        data = await self.request_game_record("index", params=dict(server=server, role_id=uid), lang=lang)

        if not equipment:
            return PartialUserStats(**data)

        character_ids = [char["id"] for char in data["avatars"]]
        character_data = await self.request_game_record(
            "character",
            method="POST",
            lang=lang,
            json=dict(character_ids=character_ids, role_id=uid, server=server),
        )
        data.update(character_data)

        return UserStats(**data)

    async def get_partial_user(self, uid: int, *, lang: str = None) -> PartialUserStats:
        """Helper alternative function to get a user without any equipment"""
        return await self.get_user(uid, lang=lang, equipment=False)

    async def get_spiral_abyss(self, uid: int, *, previous: bool = False) -> SpiralAbyss:
        """Get spiral abyss runs"""
        server = utils.recognize_server(uid)
        schedule_type = 2 if previous else 1
        data = await self.request_game_record(
            "spiralAbyss", params=dict(server=server, role_id=uid, schedule_type=schedule_type)
        )
        return SpiralAbyss(**data)

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
            return WishHistory(self, banner_type, lang=lang, authkey=authkey, limit=limit, end_id=end_id)
    
    @utils.permanent_cache('lang')
    async def get_banner_types(self, *, lang: str = None, authkey: str = None) -> Dict[int, str]:
        """Get a list of banner types"""
        data = await self.request_gacha_info(
            "getConfigList",
            lang=lang,
            authkey=authkey,
        )
        return {int(i['key']): i['name'] for i in data['gacha_type_list']}
