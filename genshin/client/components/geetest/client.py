"""Geetest client component."""

import json
import typing
from http.cookies import SimpleCookie

import aiohttp
import aiohttp.web

from genshin import constants, errors
from genshin.client import routes
from genshin.client.components import base
from genshin.utility import ds as ds_utility
from genshin.utility import geetest as geetest_utility

from . import server

__all__ = ["GeetestClient"]


class GeetestClient(base.BaseClient):
    """Geetest client component."""

    async def _web_login(
        self,
        account: str,
        password: str,
        *,
        tokenType: typing.Optional[int] = 6,
        geetest: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ) -> typing.Dict[str, typing.Any]:
        """Login with a password using web endpoint.

        Returns either data from aigis header or cookies.
        """
        headers = {**geetest_utility.WEB_LOGIN_HEADERS}
        if geetest:
            mmt_data = geetest["data"]
            session_id = geetest["session_id"]
            headers["x-rpc-aigis"] = geetest_utility.get_aigis_header(session_id, mmt_data)

        payload = {
            "account": geetest_utility.encrypt_geetest_credentials(account, self._region),
            "password": geetest_utility.encrypt_geetest_credentials(password, self._region),
            "token_type": tokenType,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.WEB_LOGIN_URL.get_url(),
                json=payload,
                headers=headers,
            ) as r:
                data = await r.json()
                cookies = {cookie.key: cookie.value for cookie in r.cookies.values()}

        if data["retcode"] == -3101:
            # Captcha triggered
            aigis = json.loads(r.headers["x-rpc-aigis"])
            aigis["data"] = json.loads(aigis["data"])
            return aigis

        if not data["data"]:
            errors.raise_for_retcode(data)

        if data["data"].get("stoken"):
            cookies["stoken"] = data["data"]["stoken"]

        self.set_cookies(cookies)

        return cookies

    async def _cn_login_by_password(
        self,
        account: str,
        password: str,
        *,
        geetest: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Login with account and password using Miyoushe loginByPassword endpoint.

        Returns data from aigis header or cookies.
        """
        headers = {
            **geetest_utility.CN_LOGIN_HEADERS,
            "ds": ds_utility.generate_dynamic_secret(constants.DS_SALT["cn_signin"]),
        }
        if geetest:
            mmt_data = geetest["data"]
            session_id = geetest["session_id"]
            headers["x-rpc-aigis"] = geetest_utility.get_aigis_header(session_id, mmt_data)

        payload = {
            "account": geetest_utility.encrypt_geetest_credentials(account, self._region),
            "password": geetest_utility.encrypt_geetest_credentials(password, self._region),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.CN_LOGIN_URL.get_url(),
                json=payload,
                headers=headers,
            ) as r:
                data = await r.json()

        if data["retcode"] == -3102:
            # Captcha triggered
            aigis = json.loads(r.headers["x-rpc-aigis"])
            aigis["data"] = json.loads(aigis["data"])
            return aigis

        if not data["data"]:
            errors.raise_for_retcode(data)

        # Parse cookies from headers
        cookies: dict[str, str] = {}
        for data in r.headers.items():
            if data[0] == "Set-Cookie":
                cookie_parser = SimpleCookie()
                cookie_parser.load(data[1])
                cookies.update({key: morsel.value for key, morsel in cookie_parser.items()})

        self.set_cookies(cookies)
        return cookies

    async def _app_login(
        self,
        account: str,
        password: str,
        *,
        geetest: typing.Optional[typing.Dict[str, typing.Any]] = None,
        ticket: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ) -> typing.Dict[str, typing.Any]:
        """Login with a password using HoYoLab app endpoint.

        Returns data from aigis header or action_ticket or cookies.
        """
        headers = {
            **geetest_utility.APP_LOGIN_HEADERS,
            "ds": ds_utility.generate_dynamic_secret(constants.DS_SALT["app_login"]),
        }
        if geetest:
            mmt_data = geetest["data"]
            session_id = geetest["session_id"]
            headers["x-rpc-aigis"] = geetest_utility.get_aigis_header(session_id, mmt_data)

        if ticket:
            ticket["verify_str"] = json.dumps(ticket["verify_str"])
            headers["x-rpc-verify"] = json.dumps(ticket)

        payload = {
            "account": geetest_utility.encrypt_geetest_credentials(account, self._region),
            "password": geetest_utility.encrypt_geetest_credentials(password, self._region),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.APP_LOGIN_URL.get_url(),
                json=payload,
                headers=headers,
            ) as r:
                data = await r.json()

        if data["retcode"] == -3101:
            # Captcha triggered
            aigis = json.loads(r.headers["x-rpc-aigis"])
            aigis["data"] = json.loads(aigis["data"])
            return aigis

        if data["retcode"] == -3239:
            # Email verification required
            verify = json.loads(r.headers["x-rpc-verify"])
            verify["verify_str"] = json.loads(verify["verify_str"])
            return verify

        if not data["data"]:
            errors.raise_for_retcode(data)

        cookies = {
            "stoken": data["data"]["token"]["token"],
            "ltuid_v2": data["data"]["user_info"]["aid"],
            "ltmid_v2": data["data"]["user_info"]["mid"],
            "account_id_v2": data["data"]["user_info"]["aid"],
            "account_mid_v2": data["data"]["user_info"]["mid"],
        }
        self.set_cookies(cookies)

        return cookies

    async def _send_verification_email(
        self,
        ticket: typing.Dict[str, typing.Any],
        *,
        geetest: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ) -> typing.Union[None, typing.Dict[str, typing.Any]]:
        """Send verification email.

        Returns None if success, aigis headers (mmt/aigis) otherwise.
        """
        headers = {**geetest_utility.EMAIL_SEND_HEADERS}
        if geetest:
            mmt_data = geetest["data"]
            session_id = geetest["session_id"]
            headers["x-rpc-aigis"] = geetest_utility.get_aigis_header(session_id, mmt_data)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.SEND_VERIFICATION_CODE_URL.get_url(),
                json={
                    "action_type": "verify_for_component",
                    "action_ticket": ticket["verify_str"]["ticket"],
                },
                headers=headers,
            ) as r:
                data = await r.json()

        if data["retcode"] == -3101:
            # Captcha triggered
            aigis = json.loads(r.headers["x-rpc-aigis"])
            aigis["data"] = json.loads(aigis["data"])
            return aigis

        if data["retcode"] != 0:
            errors.raise_for_retcode(data)

        return None

    async def _verify_email(self, code: str, ticket: typing.Dict[str, typing.Any]) -> None:
        """Verify email."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.VERIFY_EMAIL_URL.get_url(),
                json={
                    "action_type": "verify_for_component",
                    "action_ticket": ticket["verify_str"]["ticket"],
                    "email_captcha": code,
                    "verify_method": 2,
                },
                headers=geetest_utility.EMAIL_VERIFY_HEADERS,
            ) as r:
                data = await r.json()

        if data["retcode"] != 0:
            errors.raise_for_retcode(data)

        return None

    async def login_with_password(
        self,
        account: str,
        password: str,
        *,
        port: int = 5000,
        tokenType: typing.Optional[int] = 6,
        geetest_solver: typing.Optional[
            typing.Callable[
                [typing.Dict[str, typing.Any]],
                typing.Awaitable[typing.Dict[str, typing.Any]],
            ]
        ] = None,
    ) -> typing.Dict[str, str]:
        """Login with a password via web endpoint.

        Note that this will start a webserver if captcha is
        triggered and `geetest_solver` is not passed.
        """
        result = await self._web_login(account, password, tokenType=tokenType)

        if "session_id" not in result:
            # Captcha not triggered
            return result

        if geetest_solver:
            geetest = await geetest_solver(result)
        else:
            geetest = await server.solve_geetest(result, port=port)

        return await self._web_login(account, password, tokenType=tokenType, geetest=geetest)

    async def cn_login_by_password(
        self,
        account: str,
        password: str,
        *,
        port: int = 5000,
        geetest_solver: typing.Optional[
            typing.Callable[
                [typing.Dict[str, typing.Any]],
                typing.Awaitable[typing.Dict[str, typing.Any]],
            ]
        ] = None,
    ) -> typing.Dict[str, str]:
        """Login with a password via Miyoushe loginByPassword endpoint.

        Note that this will start a webserver if captcha is
        triggered and `geetest_solver` is not passed.
        """
        result = await self._cn_login_by_password(account, password)

        if "session_id" not in result:
            # Captcha not triggered
            return result

        if geetest_solver:
            geetest = await geetest_solver(result)
        else:
            geetest = await server.solve_geetest(result, port=port)

        return await self._cn_login_by_password(account, password, geetest=geetest)

    async def login_with_app_password(
        self,
        account: str,
        password: str,
        *,
        port: int = 5000,
        geetest_solver: typing.Optional[
            typing.Callable[
                [typing.Dict[str, typing.Any]],
                typing.Awaitable[typing.Dict[str, typing.Any]],
            ]
        ] = None,
    ) -> typing.Dict[str, str]:
        """Login with a password via HoYoLab app endpoint.

        Note that this will start a webserver if either of the
        following happens:

        1. Captcha is triggered and `geetest_solver` is not passed.
        2. Email verification is triggered (can happen if you
        first login with a new device).
        """
        result = await self._app_login(account, password)

        if "session_id" in result:
            # Captcha triggered
            if geetest_solver:
                geetest = await geetest_solver(result)
            else:
                geetest = await server.solve_geetest(result, port=port)

            result = await self._app_login(account, password, geetest=geetest)

        if "risk_ticket" in result:
            # Email verification required
            mmt = await self._send_verification_email(result)
            if mmt:
                if geetest_solver:
                    geetest = await geetest_solver(mmt)
                else:
                    geetest = await server.solve_geetest(mmt, port=port)

                await self._send_verification_email(result, geetest=geetest)

            await server.verify_email(self, result, port=port)
            result = await self._app_login(account, password, ticket=result)

        return result
