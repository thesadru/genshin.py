"""Geetest client component."""
import typing

import aiohttp
import aiohttp.web
import yarl

from genshin import errors
from genshin.client.components import base
from genshin.utility import geetest as geetest_utility

from . import server

__all__ = ["GeetestClient"]


WEB_LOGIN_URL = yarl.URL("https://api-account-os.hoyolab.com/account/auth/api/webLoginByPassword")


class GeetestClient(base.BaseClient):
    """Geetest client component."""

    async def login_with_geetest(
        self,
        account: str,
        password: str,
        mmt_key: str,
        geetest: typing.Dict[str, str],
        token_type: int = 0b111,
    ) -> typing.Mapping[str, str]:
        """Login with a password and a solved geetest.

        Token type is a bitfield of cookie_token, ltoken, stoken.
        """
        payload = dict(
            account=account,
            password=geetest_utility.encrypt_geetest_password(password),
            is_crypto="true",
            source="account.mihoyo.com",
            mmt_key=mmt_key,
            token_type=token_type,
        )
        payload.update(geetest)

        # we do not want to use the previous cookie manager sessions

        async with aiohttp.ClientSession() as session:
            async with session.post(WEB_LOGIN_URL, json=payload) as r:
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
