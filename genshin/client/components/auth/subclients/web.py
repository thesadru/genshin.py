"""Web sub client for AuthClient.

Covers HoYoLAB and Miyoushe web auth endpoints.
"""

import json
import typing

from genshin import constants, errors, types
from genshin.client import routes
from genshin.client.components import base
from genshin.models.auth.cookie import CNWebLoginResult, MobileLoginResult, WebLoginResult
from genshin.models.auth.geetest import SessionMMT, SessionMMTResult, SessionMMTv4
from genshin.utility import auth as auth_utility
from genshin.utility import ds as ds_utility

__all__ = ["WebAuthClient"]


class WebAuthClient(base.BaseClient):
    """Web sub client for AuthClient."""

    @typing.overload
    async def _os_web_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = ...,
        token_type: typing.Optional[int] = ...,
        mmt_result: SessionMMTResult,
    ) -> WebLoginResult: ...

    @typing.overload
    async def _os_web_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = ...,
        token_type: typing.Optional[int] = ...,
        mmt_result: None = ...,
    ) -> typing.Union[SessionMMT, WebLoginResult]: ...

    @base.region_specific(types.Region.OVERSEAS)
    async def _os_web_login(
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = False,
        token_type: typing.Optional[int] = 6,
        mmt_result: typing.Optional[SessionMMTResult] = None,
    ) -> typing.Union[SessionMMT, WebLoginResult]:
        """Login with a password using web endpoint.

        Returns either data from aigis header or cookies.
        """
        headers = {**auth_utility.WEB_LOGIN_HEADERS}
        if mmt_result:
            headers["x-rpc-aigis"] = mmt_result.to_aigis_header()

        payload = {
            "account": account if encrypted else auth_utility.encrypt_credentials(account, 1),
            "password": password if encrypted else auth_utility.encrypt_credentials(password, 1),
            "token_type": token_type,
        }

        async with self.cookie_manager.create_session() as session:
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
            return SessionMMT(**aigis)

        if not data["data"]:
            errors.raise_for_retcode(data)

        if data["data"].get("stoken"):
            cookies["stoken"] = data["data"]["stoken"]

        self.set_cookies(cookies)
        return WebLoginResult(**cookies)

    @typing.overload
    async def _cn_web_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = ...,
        mmt_result: SessionMMTResult,
    ) -> CNWebLoginResult: ...

    @typing.overload
    async def _cn_web_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = ...,
        mmt_result: None = ...,
    ) -> typing.Union[SessionMMT, CNWebLoginResult]: ...

    @base.region_specific(types.Region.CHINESE)
    async def _cn_web_login(
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = False,
        mmt_result: typing.Optional[SessionMMTResult] = None,
    ) -> typing.Union[SessionMMT, CNWebLoginResult]:
        """
        Login with account and password using Miyoushe loginByPassword endpoint.

        Returns data from aigis header or cookies.
        """
        headers = {
            **auth_utility.CN_LOGIN_HEADERS,
            "ds": ds_utility.generate_dynamic_secret(constants.DS_SALT["cn_signin"]),
        }
        if mmt_result:
            headers["x-rpc-aigis"] = mmt_result.to_aigis_header()

        payload = {
            "account": account if encrypted else auth_utility.encrypt_credentials(account, 2),
            "password": password if encrypted else auth_utility.encrypt_credentials(password, 2),
        }

        async with self.cookie_manager.create_session() as session:
            async with session.post(
                routes.CN_WEB_LOGIN_URL.get_url(),
                json=payload,
                headers=headers,
            ) as r:
                data = await r.json()

        if data["retcode"] == -3102:
            # Captcha triggered
            aigis = json.loads(r.headers["x-rpc-aigis"])
            return SessionMMT(**aigis)

        if not data["data"]:
            errors.raise_for_retcode(data)

        cookies = {cookie.key: cookie.value for cookie in r.cookies.values()}
        self.set_cookies(cookies)

        return CNWebLoginResult(**cookies)

    async def _send_mobile_otp(
        self,
        mobile: str,
        *,
        encrypted: bool = False,
        mmt_result: typing.Optional[SessionMMTResult] = None,
    ) -> typing.Union[None, SessionMMTv4]:
        """Attempt to send OTP to the provided mobile number.

        May return aigis headers if captcha is triggered, None otherwise.
        """
        headers = {
            **auth_utility.CN_LOGIN_HEADERS,
            "ds": ds_utility.generate_dynamic_secret(constants.DS_SALT["cn_signin"]),
        }
        if mmt_result:
            headers["x-rpc-aigis"] = mmt_result.to_aigis_header()

        payload = {
            "mobile": mobile if encrypted else auth_utility.encrypt_credentials(mobile, 2),
            "area_code": auth_utility.encrypt_credentials("+86", 2),
        }

        async with self.cookie_manager.create_session() as session:
            async with session.post(
                routes.MOBILE_OTP_URL.get_url(),
                json=payload,
                headers=headers,
            ) as r:
                data = await r.json()

        if data["retcode"] == -3101:
            # Captcha triggered
            aigis = json.loads(r.headers["x-rpc-aigis"])
            return SessionMMTv4(**aigis)

        if not data["data"]:
            errors.raise_for_retcode(data)

        return None

    async def _login_with_mobile_otp(self, mobile: str, otp: str, *, encrypted: bool = False) -> MobileLoginResult:
        """Login with OTP and mobile number.

        Returns cookies if OTP matches the one sent, raises an error otherwise.
        """
        headers = {
            **auth_utility.CN_LOGIN_HEADERS,
            "ds": ds_utility.generate_dynamic_secret(constants.DS_SALT["cn_signin"]),
        }

        payload = {
            "mobile": mobile if encrypted else auth_utility.encrypt_credentials(mobile, 2),
            "area_code": auth_utility.encrypt_credentials("+86", 2),
            "captcha": otp,
        }

        async with self.cookie_manager.create_session() as session:
            async with session.post(
                routes.MOBILE_LOGIN_URL.get_url(),
                json=payload,
                headers=headers,
            ) as r:
                data = await r.json()

        if not data["data"]:
            errors.raise_for_retcode(data)

        cookies = {cookie.key: cookie.value for cookie in r.cookies.values()}
        self.set_cookies(cookies)

        return MobileLoginResult(**cookies)
