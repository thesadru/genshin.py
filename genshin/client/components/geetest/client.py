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
        geetest: dict[str, str],
        token_type: int = 4,
    ) -> typing.Mapping[str, str]:
        """Login with a password and a solved geetest."""
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

        if not data["data"]:
            errors.raise_for_retcode(data)

        account_id: str = data["data"]["account_info"]["account_id"]

        cookies = {cookie.key: cookie.value for cookie in r.cookies.values()}
        cookies.update(account_id=account_id, ltuid=account_id)

        self.set_cookies(cookies)

        return cookies

    async def login_with_password(self, account: str, password: str, *, port: int = 5000) -> typing.Mapping[str, str]:
        """Login with a password.

        This will start a webserver.
        """
        return await server.login_with_app(self, account, password, port=port)
