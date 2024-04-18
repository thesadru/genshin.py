"""App sub client for AuthClient.

Covers HoYoLAB and Miyoushe app auth endpoints.
"""

import json
import random
import typing
from string import ascii_letters, digits

import aiohttp

from genshin import constants, errors
from genshin.client import routes
from genshin.client.components import base
from genshin.models.auth.cookie import AppLoginResult
from genshin.models.auth.geetest import SessionMMT, SessionMMTResult
from genshin.models.auth.qrcode import QRCodeCheckResult, QRCodeCreationResult
from genshin.models.auth.verification import ActionTicket
from genshin.utility import auth as auth_utility
from genshin.utility import ds as ds_utility

__all__ = ["AppAuthClient"]


class AppAuthClient(base.BaseClient):
    """App sub client for AuthClient."""

    @typing.overload
    async def _app_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        mmt_result: SessionMMTResult,
        ticket: None = ...,
    ) -> typing.Union[AppLoginResult, ActionTicket]: ...

    @typing.overload
    async def _app_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        mmt_result: None = ...,
        ticket: ActionTicket,
    ) -> AppLoginResult: ...

    @typing.overload
    async def _app_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        mmt_result: None = ...,
        ticket: None = ...,
    ) -> typing.Union[AppLoginResult, SessionMMT, ActionTicket]: ...

    async def _app_login(
        self,
        account: str,
        password: str,
        *,
        mmt_result: typing.Optional[SessionMMTResult] = None,
        ticket: typing.Optional[ActionTicket] = None,
    ) -> typing.Union[AppLoginResult, SessionMMT, ActionTicket]:
        """Login with a password using HoYoLab app endpoint.

        Returns
        -------
        - Cookies if login is successful.
        - SessionMMT if captcha is triggered.
        - ActionTicket if email verification is required.
        """
        headers = {
            **auth_utility.APP_LOGIN_HEADERS,
            "ds": ds_utility.generate_dynamic_secret(constants.DS_SALT["app_login"]),
        }
        if mmt_result:
            headers["x-rpc-aigis"] = mmt_result.to_aigis_header()

        if ticket:
            headers["x-rpc-verify"] = ticket.to_rpc_verify_header()

        payload = {
            "account": auth_utility.encrypt_geetest_credentials(account, 1),
            "password": auth_utility.encrypt_geetest_credentials(password, 1),
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
            return SessionMMT(**aigis)

        if data["retcode"] == -3239:
            # Email verification required
            action_ticket = json.loads(r.headers["x-rpc-verify"])
            return ActionTicket(**action_ticket)

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

        return AppLoginResult(**cookies)

    async def _send_verification_email(
        self,
        ticket: ActionTicket,
        *,
        mmt_result: typing.Optional[SessionMMTResult] = None,
    ) -> typing.Union[None, SessionMMT]:
        """Send verification email.

        Returns None if success, SessionMMT data if geetest triggered.
        """
        headers = {**auth_utility.EMAIL_SEND_HEADERS}
        if mmt_result:
            headers["x-rpc-aigis"] = mmt_result.to_aigis_header()

        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.SEND_VERIFICATION_CODE_URL.get_url(),
                json={
                    "action_type": "verify_for_component",
                    "action_ticket": ticket.verify_str.ticket,
                },
                headers=headers,
            ) as r:
                data = await r.json()

        if data["retcode"] == -3101:
            # Captcha triggered
            aigis = json.loads(r.headers["x-rpc-aigis"])
            return SessionMMT(**aigis)

        if data["retcode"] != 0:
            errors.raise_for_retcode(data)

        return None

    async def _verify_email(self, code: str, ticket: ActionTicket) -> None:
        """Verify email."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.VERIFY_EMAIL_URL.get_url(),
                json={
                    "action_type": "verify_for_component",
                    "action_ticket": ticket.verify_str.ticket,
                    "email_captcha": code,
                    "verify_method": 2,
                },
                headers=auth_utility.EMAIL_VERIFY_HEADERS,
            ) as r:
                data = await r.json()

        if data["retcode"] != 0:
            errors.raise_for_retcode(data)

        return None

    async def _create_qrcode(self) -> QRCodeCreationResult:
        """Create a QR code for login."""
        if self.default_game is None:
            raise RuntimeError("No default game set.")

        app_id = constants.APP_IDS[self.default_game][self.region]
        device_id = "".join(random.choices(ascii_letters + digits, k=64))

        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.CREATE_QRCODE_URL.get_url(),
                json={"app_id": app_id, "device": device_id},
            ) as r:
                data = await r.json()

        if not data["data"]:
            errors.raise_for_retcode(data)

        url: str = data["data"]["url"]
        return QRCodeCreationResult(
            app_id=app_id,
            ticket=url.split("ticket=")[1],
            device_id=device_id,
            url=url,
        )

    async def _check_qrcode(self, app_id: str, device_id: str, ticket: str) -> QRCodeCheckResult:
        """Check the status of a QR code login."""
        payload = {
            "app_id": app_id,
            "device": device_id,
            "ticket": ticket,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.CHECK_QRCODE_URL.get_url(),
                json=payload,
            ) as r:
                data = await r.json()

        if not data["data"]:
            errors.raise_for_retcode(data)

        return QRCodeCheckResult(**data["data"])
