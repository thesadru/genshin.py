"""Geetest client component."""
import typing
import json

import aiohttp
import aiohttp.web
import yarl
import base64

from genshin import errors
from genshin.client.components import base
from genshin.utility import geetest as geetest_utility

from . import server

__all__ = ["GeetestClient"]


WEB_LOGIN_URL = yarl.URL("https://sg-public-api.hoyolab.com/account/ma-passport/api/webLoginByPassword")


class GeetestClient(base.BaseClient):
    """Geetest client component."""

    async def login_with_geetest(
        self,
        account: str,
        password: str,
        session_id: str,
        geetest: typing.Dict[str, str]
    ) -> typing.Mapping[str, str]:
        """Login with a password and a solved geetest.

        Token type is a bitfield of cookie_token, ltoken, stoken.
        """

        payload = {
            "account": geetest_utility.encrypt_geetest_password(account),
            "password": geetest_utility.encrypt_geetest_password(password),
            "token_type": 6
        }

        # we do not want to use the previous cookie manager sessions

        async with aiohttp.ClientSession() as session:
            async with session.post(WEB_LOGIN_URL, json=payload, headers={
                **geetest_utility.HEADERS,
                "x-rpc-aigis": f"{session_id};{base64.b64encode(json.dumps(geetest).encode()).decode()}",
            }) as r:
                data = await r.json()
                cookies = {cookie.key: cookie.value for cookie in r.cookies.values()}

        if not data["data"]:
            errors.raise_for_retcode(data)

        if data["data"].get("stoken"):
            cookies["stoken"] = data["data"]["stoken"]

        self.set_cookies(cookies)

        return cookies

    async def login_with_password(self, account: str, password: str, *, port: int = 5000) -> typing.Mapping[str, str]:
        """Login with a password.

        This will start a webserver.
        """
        return await server.login_with_app(self, account, password, port=port)
