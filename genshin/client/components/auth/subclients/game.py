"""Game sub client for AuthClient.

Covers OS and CN game auth endpoints.
"""

import json
import typing

import aiohttp

from genshin import constants, errors, types
from genshin.client import routes
from genshin.client.components import base
from genshin.models.auth.geetest import RiskyCheckMMT, RiskyCheckResult, RiskyCheckMMTResult
from genshin.models.auth.responses import ShieldLoginResponse
from genshin.models.auth.cookie import DeviceGrantResult, GameLoginResult
from genshin.utility import auth as auth_utility

__all__ = ["GameAuthClient"]


class GameAuthClient(base.BaseClient):
    """Game sub client for AuthClient."""

    async def _risky_check(
        self, action_type: str, api_name: str, *, username: typing.Optional[str] = None
    ) -> RiskyCheckResult:
        """Check if the given action (endpoint) is risky (whether captcha verification is required)."""
        payload = {"action_type": action_type, "api_name": api_name}
        if username:
            payload["username"] = username

        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.GAME_RISKY_CHECK_URL.get_url(self.region), json=payload, headers=auth_utility.RISKY_CHECK_HEADERS
            ) as r:
                data = await r.json()

        if not data["data"]:
            errors.raise_for_retcode(data)

        return RiskyCheckResult(**data["data"])

    @typing.overload
    async def _shield_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        mmt_result: RiskyCheckMMTResult,
    ) -> ShieldLoginResponse: ...

    @typing.overload
    async def _shield_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        mmt_result: None = ...,
    ) -> typing.Union[ShieldLoginResponse, RiskyCheckMMT]: ...

    async def _shield_login(
        self, account: str, password: str, *, mmt_result: typing.Optional[RiskyCheckMMTResult] = None
    ) -> typing.Union[ShieldLoginResponse, RiskyCheckMMT]:
        """Log in with the given account and password.

        Returns MMT if geetest verification is required.
        """
        if self.default_game is None:
            raise ValueError("No default game set.")

        headers = auth_utility.SHIELD_LOGIN_HEADERS.copy()
        if mmt_result:
            headers["x-rpc-risky"] = mmt_result.to_rpc_risky()
        else:
            # Check if geetest is required
            check_result = await self._risky_check("login", "/shield/api/login", username=account)
            if check_result.mmt:
                return check_result.to_mmt()
            else:
                headers["x-rpc-risky"] = auth_utility.generate_risky_header(check_result.id)

        payload = {"account": account, "password": password, "is_crypto": True}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.SHIELD_LOGIN_URL.get_url(self.region, self.default_game), json=payload, headers=headers
            ) as r:
                data = await r.json()

        if not data["data"]:
            errors.raise_for_retcode(data)

        return ShieldLoginResponse(**data["data"])

    @typing.overload
    async def _send_game_verification_email(  # noqa: D102 missing docstring in overload?
        self,
        action_ticket: str,
        *,
        mmt_result: RiskyCheckMMTResult,
    ) -> None: ...

    @typing.overload
    async def _send_game_verification_email(  # noqa: D102 missing docstring in overload?
        self,
        action_ticket: str,
        *,
        mmt_result: None = ...,
    ) -> typing.Union[None, RiskyCheckMMT]: ...

    async def _send_game_verification_email(
        self, action_ticket: str, *, mmt_result: typing.Optional[RiskyCheckMMTResult] = None
    ) -> typing.Union[None, RiskyCheckMMT]:
        """Send email verification code.

        Returns `None` if success, `RiskyCheckMMT` if geetest verification is required.
        """
        headers = auth_utility.GRANT_TICKET_HEADERS.copy()
        if mmt_result:
            headers["x-rpc-risky"] = mmt_result.to_rpc_risky()
        else:
            # Check if geetest is required
            check_result = await self._risky_check("device_grant", "/device/api/preGrantByTicket")
            if check_result.mmt:
                return check_result.to_mmt()
            else:
                headers["x-rpc-risky"] = auth_utility.generate_risky_header(check_result.id)

        payload = {
            "way": "Way_Email",
            "action_ticket": action_ticket,
            "device": {
                "device_model": "iPhone15,4",
                "device_id": auth_utility.DEVICE_ID,
                "client": 1,
                "device_name": "iPhone",
            },
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.PRE_GRANT_TICKET_URL.get_url(self.region), json=payload, headers=headers
            ) as r:
                data = await r.json()

        if data["retcode"] != 0:
            errors.raise_for_retcode(data)

        return None

    async def _verify_game_email(self, code: str, action_ticket: str) -> DeviceGrantResult:
        """Verify the email code."""
        payload = {"code": code, "ticket": action_ticket}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.DEVICE_GRANT_URL.get_url(self.region), json=payload, headers=auth_utility.GRANT_TICKET_HEADERS
            ) as r:
                data = await r.json()

        return DeviceGrantResult(**data["data"])

    @base.region_specific(types.Region.OVERSEAS)
    async def _os_game_login(self, uid: str, game_token: str) -> GameLoginResult:
        """Log in to the game."""
        if self.default_game is None:
            raise ValueError("No default game set.")

        payload = {
            "channel_id": 1,
            "device": auth_utility.DEVICE_ID,
            "app_id": constants.APP_IDS[self.default_game][self.region],
        }
        payload["data"] = json.dumps({"uid": uid, "token": game_token, "guest": False})
        payload["sign"] = auth_utility.generate_sign(payload, constants.APP_KEYS[self.default_game][self.region])

        async with aiohttp.ClientSession() as session:
            async with session.post(
                routes.GAME_LOGIN_URL.get_url(self.region, self.default_game),
                json=payload,
                headers=auth_utility.GAME_LOGIN_HEADERS,
            ) as r:
                data = await r.json()

        if not data["data"]:
            errors.raise_for_retcode(data)

        return GameLoginResult(**data["data"])
