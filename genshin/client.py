import asyncio
from genshin.models.character import Character
from genshin.models import UserStats
import hashlib
import random
import string
import time
from typing import Any, ClassVar, Dict, List, Mapping, Union

import aiohttp
from yarl import URL


def generate_ds_token(salt: str) -> str:
    """Creates a new ds token for authentication."""
    t = int(time.time())
    r = "".join(random.choices(string.ascii_letters, k=6))
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()
    return f"{t},{r},{h}"


def recognize_server(uid: int) -> str:
    """Recognizes which server a UID is from."""
    server = {
        "1": "cn_gf01",
        "5": "cn_qd01",
        "6": "os_usa",
        "7": "os_euro",
        "8": "os_asia",
        "9": "os_cht",
    }.get(str(uid)[0])

    if server:
        return server
    else:
        raise Exception(f"UID {uid} isn't associated with any server")


class GenshinClient:
    OS_DS_SALT: ClassVar[str] = "6cqshh5dhw73bzxn20oexa9k516chk7s"
    CN_DS_SALT: ClassVar[str] = "14bmu1mz0yuljprsfgpvjh3ju2ni468r"
    OS_BBS_URL: ClassVar[str] = "https://bbs-api-os.hoyolab.com/"
    CN_TAKUMI_URL: ClassVar[str] = "https://api-takumi.mihoyo.com/"

    USER_AGENT: ClassVar[str] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    def __init__(self, cookies: Dict[str, str], lang: str = "en-us") -> None:
        self.cookies = cookies
        self.lang = lang

    @property
    def session(self) -> aiohttp.ClientSession:
        """The current client session, created when needed"""
        if not hasattr(self, "_session"):
            self._session = aiohttp.ClientSession(cookies=self.cookies)

        return self._session

    @property
    def hoyolab_uid(self) -> int:
        """The logged-in user's hoyolab uid
        
        Defaults to 0 when not logged in
        """
        for cookie in self.session.cookie_jar:
            if cookie.key == "ltuid":
                return int(cookie.value)

        return 0

    def create_headers(self, chinese: bool = False, lang: str = None) -> Dict[str, str]:
        """The headers required for a request"""
        return {
            "user-agent": self.USER_AGENT,
            "x-rpc-app_version": "2.7.0" if chinese else "1.5.0",
            "x-rpc-client_type": "5" if chinese else "4",
            "x-rpc-language": lang or self.lang,
            "ds": generate_ds_token(self.CN_DS_SALT if chinese else self.OS_DS_SALT),
        }

    def create_url(self, endpoint: Union[str, URL], chinese: bool = False) -> URL:
        """Url pointing to a game record endpoint"""
        base_url = URL(self.CN_TAKUMI_URL if chinese else self.OS_BBS_URL)
        return base_url.join(URL(endpoint))

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

    async def request(
        self,
        endpoint: str,
        method: str = "GET",
        chinese: bool = False,
        lang: str = None,
        params: Mapping[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request and return a parsed dictionary response"""
        headers = self.create_headers(chinese, lang)
        url = self.create_url(endpoint, chinese).update_query(params)

        async with self.session.request(method, url, headers=headers, **kwargs) as r:
            print(r.request_info.url)
            print(dict(r.request_info.headers))
            data = await r.json()

        if data["retcode"] == 0:
            return data["data"]
        else:
            raise Exception(f"{data['retcode']} - {data['message']}")

    async def get_user_stats(self, uid: int) -> UserStats:
        """Get a user's stats"""
        server = recognize_server(uid)
        data = await self.request("game_record/genshin/api/index", params=dict(server=server, role_id=uid))
        return UserStats(**data)

    async def get_characters(self, uid: int, character_ids: List[int] = None, lang: str = None) -> List[Character]:
        """Get a list of user's characters along with all their equipment"""
        if character_ids is None:
            stats = await self.get_user_stats(uid)
            character_ids = [char.id for char in stats.characters]

        server = recognize_server(uid)
        data = await self.request(
            "game_record/genshin/api/character",
            method="POST",
            lang=lang,
            json=dict(character_ids=character_ids, role_id=uid, server=server),
        )
        return [Character(**i) for i in data["avatars"]]


async def test():
    import os
    from devtools import debug

    client = GenshinClient({"ltuid": os.environ["GS_LTUID"], "ltoken": os.environ["GS_LTOKEN"]})
    async with client:
        data = await client.get_user_stats(710785423)
        debug(data)


if __name__ == "__main__":
    from functools import wraps
    from asyncio.proactor_events import _ProactorBasePipeTransport

    def silence_event_loop_closed(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except RuntimeError as e:
                if str(e) != "Event loop is closed":
                    raise

        return wrapper
    
    _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
    
    asyncio.run(test())
