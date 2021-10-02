
from typing import Any, ClassVar, Dict, Literal, Union, overload, Optional

import aiohttp
from yarl import URL

from . import utils
from .models import *
from .paginator import WishHistory


class GenshinClient:
    """A simple http client for genshin endpoints"""

    OS_DS_SALT: ClassVar[str] = "6cqshh5dhw73bzxn20oexa9k516chk7s"
    CN_DS_SALT: ClassVar[str] = "14bmu1mz0yuljprsfgpvjh3ju2ni468r"

    OS_BBS_URL = "https://bbs-api-os.hoyolab.com/game_record/genshin/api"
    CN_TAKUMI_URL = "https://api-takumi.mihoyo.com/game_record/genshin/api"
    GACHA_INFO_URL = "https://hk4e-api-os.mihoyo.com/event/gacha_info/api/"

    USER_AGENT: ClassVar[
        str
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    def __init__(self, cookies: Dict[str, str], lang: str = "en-us", authkey: str = None) -> None:
        self.cookies = cookies
        self.authkey = authkey
        self.lang = lang

    @property
    def session(self) -> aiohttp.ClientSession:
        """The current client session, created when needed"""
        if not hasattr(self, "_session"):
            self._session = aiohttp.ClientSession(cookies=self.cookies)

        return self._session

    @property
    def hoyolab_uid(self) -> Optional[int]:
        """The logged-in user's hoyolab uid"""
        for cookie in self.session.cookie_jar:
            if cookie.key == "ltuid":
                return int(cookie.value)

        return None

    async def close(self):
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

        async with self.session.request(method, url, **kwargs) as r:
            print(r.url)
            data = await r.json()

        if data["retcode"] == 0:
            return data["data"]
        else:
            raise Exception(f"{data['retcode']} - {data['message']}")

    async def request_game_record(
        self, endpoint: str, method: str = "GET", chinese: bool = False, lang: str = None, **kwargs
    ) -> Dict[str, Any]:
        """Make a request towards the game record endpoint

        User stats related data
        """
        base_url = URL(self.CN_TAKUMI_URL if chinese else self.OS_BBS_URL)
        url = base_url.join(URL(endpoint))

        headers = {
            "user-agent": self.USER_AGENT,
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

        return await self.request(url, method, params=params)

    # GAME RECORD:

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

    def wish_history(
        self,
        banner_type: Union[int, BannerType] = None,
        *,
        limit: int = None,
        authkey: str = None,
        end_id: int = 0,
        lang: str = None,
    ):
        if banner_type is not None:
            return WishHistory(self, banner_type, lang=lang, authkey=authkey, limit=limit, end_id=end_id)
        
        raise NotImplementedError("Wish History merge not implemented yet.")
