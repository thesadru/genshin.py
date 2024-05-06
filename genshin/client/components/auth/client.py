"""Main auth client."""

import asyncio
import logging
import typing

import aiohttp

from genshin import errors, types
from genshin.client import routes
from genshin.client.components import base
from genshin.client.manager import managers
from genshin.client.manager.cookie import fetch_cookie_token_with_game_token, fetch_stoken_with_game_token
from genshin.models.auth.cookie import (
    AppLoginResult,
    CNWebLoginResult,
    GameLoginResult,
    MobileLoginResult,
    QRLoginResult,
    WebLoginResult,
)
from genshin.models.auth.geetest import MMT, RiskyCheckMMT, RiskyCheckMMTResult, SessionMMT, SessionMMTResult
from genshin.models.auth.qrcode import QRCodeStatus
from genshin.models.auth.verification import ActionTicket
from genshin.types import Game
from genshin.utility import auth as auth_utility
from genshin.utility import ds as ds_utility

from . import server, subclients

__all__ = ["AuthClient"]

LOGGER_ = logging.getLogger(__name__)


class AuthClient(subclients.AppAuthClient, subclients.WebAuthClient, subclients.GameAuthClient):
    """Auth client component."""

    @base.region_specific(types.Region.OVERSEAS)
    async def os_login_with_password(
        self,
        account: str,
        password: str,
        *,
        port: int = 5000,
        encrypted: bool = False,
        token_type: typing.Optional[int] = 6,
        geetest_solver: typing.Optional[typing.Callable[[SessionMMT], typing.Awaitable[SessionMMTResult]]] = None,
    ) -> WebLoginResult:
        """Login with a password via web endpoint.

        Note that this will start a webserver if captcha is
        triggered and `geetest_solver` is not passed.
        """
        result = await self._os_web_login(account, password, encrypted=encrypted, token_type=token_type)

        if not isinstance(result, SessionMMT):
            # Captcha not triggered
            return result

        if geetest_solver:
            mmt_result = await geetest_solver(result)
        else:
            mmt_result = await server.solve_geetest(result, port=port)

        return await self._os_web_login(
            account, password, encrypted=encrypted, token_type=token_type, mmt_result=mmt_result
        )

    @base.region_specific(types.Region.CHINESE)
    async def cn_login_with_password(
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = False,
        port: int = 5000,
        geetest_solver: typing.Optional[typing.Callable[[SessionMMT], typing.Awaitable[SessionMMTResult]]] = None,
    ) -> CNWebLoginResult:
        """Login with a password via Miyoushe loginByPassword endpoint.

        Note that this will start a webserver if captcha is
        triggered and `geetest_solver` is not passed.
        """
        result = await self._cn_web_login(account, password, encrypted=encrypted)

        if not isinstance(result, SessionMMT):
            # Captcha not triggered
            return result

        if geetest_solver:
            mmt_result = await geetest_solver(result)
        else:
            mmt_result = await server.solve_geetest(result, port=port)

        return await self._cn_web_login(account, password, encrypted=encrypted, mmt_result=mmt_result)

    @base.region_specific(types.Region.OVERSEAS)
    async def check_mobile_number_validity(self, mobile: str) -> bool:
        """Check if a mobile number is valid (it's registered on Miyoushe).

        Returns True if the mobile number is valid, False otherwise.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                routes.CHECK_MOBILE_VALIDITY_URL.get_url(),
                params={"mobile": mobile},
            ) as r:
                data = await r.json()

        return data["data"]["status"] != data["data"]["is_registable"]

    @base.region_specific(types.Region.CHINESE)
    async def login_with_mobile_number(
        self,
        mobile: str,
        *,
        encrypted: bool = False,
        port: int = 5000,
    ) -> MobileLoginResult:
        """Login with mobile number, returns cookies.

        Only works for Chinese region (Miyoushe) users, do not include
        area code (+86) in the mobile number.

        Steps:
        1. Sends OTP to the provided mobile number.
        2. If captcha is triggered, prompts the user to solve it.
        3. Lets user enter the OTP.
        4. Logs in with the OTP.
        5. Returns cookies.
        """
        result = await self._send_mobile_otp(mobile)

        if isinstance(result, SessionMMT):
            # Captcha triggered
            mmt_result = await server.solve_geetest(result, port=port)
            await self._send_mobile_otp(mobile, mmt_result=mmt_result)

        otp = await server.enter_code(port=port)
        return await self._login_with_mobile_otp(mobile, otp)

    @base.region_specific(types.Region.OVERSEAS)
    async def login_with_app_password(
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = False,
        port: int = 5000,
        geetest_solver: typing.Optional[typing.Callable[[SessionMMT], typing.Awaitable[SessionMMTResult]]] = None,
    ) -> AppLoginResult:
        """Login with a password via HoYoLab app endpoint.

        Note that this will start a webserver if either of the
        following happens:

        1. Captcha is triggered and `geetest_solver` is not passed.
        2. Email verification is triggered (can happen if you
        first login with a new device).
        """
        result = await self._app_login(account, password, encrypted=encrypted)

        if isinstance(result, SessionMMT):
            # Captcha triggered
            if geetest_solver:
                mmt_result = await geetest_solver(result)
            else:
                mmt_result = await server.solve_geetest(result, port=port)

            result = await self._app_login(account, password, encrypted=encrypted, mmt_result=mmt_result)

        if isinstance(result, ActionTicket):
            # Email verification required
            mmt = await self._send_verification_email(result)
            if mmt:
                if geetest_solver:
                    mmt_result = await geetest_solver(mmt)
                else:
                    mmt_result = await server.solve_geetest(mmt, port=port)

                await asyncio.sleep(2)  # Add delay to prevent [-3206]
                await self._send_verification_email(result, mmt_result=mmt_result)

            code = await server.enter_code(port=port)
            await self._verify_email(code, result)

            result = await self._app_login(account, password, encrypted=encrypted, ticket=result)

        return result

    @base.region_specific(types.Region.CHINESE)
    async def login_with_qrcode(self) -> QRLoginResult:
        """Login with QR code, only available for Miyoushe users."""
        import qrcode
        import qrcode.image.pil
        from qrcode.constants import ERROR_CORRECT_L

        creation_result = await self._create_qrcode()
        qrcode_: qrcode.image.pil.PilImage = qrcode.make(creation_result.url, error_correction=ERROR_CORRECT_L)  # type: ignore
        qrcode_.show()

        scanned = False
        while True:
            check_result = await self._check_qrcode(
                creation_result.app_id, creation_result.device_id, creation_result.ticket
            )
            if check_result.status == QRCodeStatus.SCANNED and not scanned:
                LOGGER_.info("QR code scanned")
                scanned = True
            elif check_result.status == QRCodeStatus.CONFIRMED:
                LOGGER_.info("QR code login confirmed")
                break

            await asyncio.sleep(2)

        raw_data = check_result.payload.raw
        assert raw_data is not None

        cookie_token = await fetch_cookie_token_with_game_token(
            game_token=raw_data.game_token, account_id=raw_data.account_id
        )
        stoken = await fetch_stoken_with_game_token(game_token=raw_data.game_token, account_id=int(raw_data.account_id))

        cookies = {
            "stoken_v2": stoken.token,
            "ltuid": stoken.aid,
            "account_id": stoken.aid,
            "ltmid": stoken.mid,
            "cookie_token": cookie_token,
        }
        self.set_cookies(cookies)
        return QRLoginResult(**cookies)

    @base.region_specific(types.Region.CHINESE)
    @managers.no_multi
    async def create_mmt(self) -> MMT:
        """Create a geetest challenge."""
        is_genshin = self.game is Game.GENSHIN
        headers = {
            "DS": ds_utility.generate_create_geetest_ds(),
            "x-rpc-challenge_game": "2" if is_genshin else "6",
            "x-rpc-page": "v4.1.5-ys_#ys" if is_genshin else "v1.4.1-rpg_#/rpg",
            "x-rpc-tool-verison": "v4.1.5-ys" if is_genshin else "v1.4.1-rpg",
            **auth_utility.CREATE_MMT_HEADERS,
        }

        assert isinstance(self.cookie_manager, managers.CookieManager)
        async with self.cookie_manager.create_session() as session:
            async with session.get(
                routes.CREATE_MMT_URL.get_url(), headers=headers, cookies=self.cookie_manager.cookies
            ) as r:
                data = await r.json()

        if not data["data"]:
            errors.raise_for_retcode(data)

        return MMT(**data["data"])

    @base.region_specific(types.Region.OVERSEAS)
    async def os_game_login(
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = False,
        port: int = 5000,
        geetest_solver: typing.Optional[typing.Callable[[RiskyCheckMMT], typing.Awaitable[RiskyCheckMMTResult]]] = None,
    ) -> GameLoginResult:
        """Perform a login to the game."""
        result = await self._shield_login(account, password, encrypted=encrypted)

        if isinstance(result, RiskyCheckMMT):
            if geetest_solver:
                mmt_result = await geetest_solver(result)
            else:
                mmt_result = await server.solve_geetest(result, port=port)

            result = await self._shield_login(account, password, encrypted=encrypted, mmt_result=mmt_result)

        if not result.device_grant_required:
            return await self._os_game_login(result.account.uid, result.account.token)

        mmt = await self._send_game_verification_email(result.account.device_grant_ticket)
        if mmt:
            if geetest_solver:
                mmt_result = await geetest_solver(mmt)
            else:
                mmt_result = await server.solve_geetest(mmt, port=port)

            await self._send_game_verification_email(result.account.device_grant_ticket, mmt_result=mmt_result)

        code = await server.enter_code()
        verification_result = await self._verify_game_email(code, result.account.device_grant_ticket)

        return await self._os_game_login(result.account.uid, verification_result.game_token)
