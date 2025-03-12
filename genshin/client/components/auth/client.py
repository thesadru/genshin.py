"""Main auth client."""

import asyncio
import json
import logging
import random
import time
import typing
import uuid
from string import digits

import aiohttp

from genshin import constants, errors, types
from genshin.client import routes
from genshin.client.components import base
from genshin.client.manager import managers
from genshin.models.auth.cookie import (
    AppLoginResult,
    CNWebLoginResult,
    GameLoginResult,
    MobileLoginResult,
    QRLoginResult,
    WebLoginResult,
)
from genshin.models.auth.geetest import MMT, MMTResult, RiskyCheckMMT, RiskyCheckMMTResult, SessionMMT, SessionMMTResult
from genshin.models.auth.qrcode import QRCodeStatus
from genshin.models.auth.verification import ActionTicket
from genshin.utility import auth as auth_utility
from genshin.utility import ds as ds_utility

from . import server, subclients

__all__ = ["AuthClient"]

LOGGER_ = logging.getLogger(__name__)


class AuthClient(subclients.AppAuthClient, subclients.WebAuthClient, subclients.GameAuthClient):
    """Auth client component."""

    async def login_with_password(
        self,
        account: str,
        password: str,
        *,
        port: int = 5000,
        encrypted: bool = False,
        geetest_solver: typing.Optional[typing.Callable[[SessionMMT], typing.Awaitable[SessionMMTResult]]] = None,
    ) -> typing.Union[WebLoginResult, CNWebLoginResult]:
        """Login with a password via web endpoint.

        Endpoint is chosen based on client region.

        Note that this will start a webserver if captcha is
        triggered and `geetest_solver` is not passed.

        Raises
        ------
        - AccountLoginFail: Invalid password provided.
        - AccountDoesNotExist: Invalid email/username.
        """
        if self.region is types.Region.CHINESE:
            return await self.cn_login_with_password(
                account, password, encrypted=encrypted, port=port, geetest_solver=geetest_solver
            )

        return await self.os_login_with_password(
            account, password, port=port, encrypted=encrypted, geetest_solver=geetest_solver
        )

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

        Raises
        ------
        - AccountLoginFail: Invalid password provided.
        - AccountDoesNotExist: Invalid email/username.
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
        async with self.cookie_manager.create_session() as session:
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
        result = await self._send_mobile_otp(mobile, encrypted=encrypted)

        if isinstance(result, SessionMMT):
            # Captcha triggered
            mmt_result = await server.solve_geetest(result, port=port)
            await self._send_mobile_otp(mobile, encrypted=encrypted, mmt_result=mmt_result)

        otp = await server.enter_code(port=port)
        return await self._login_with_mobile_otp(mobile, otp, encrypted=encrypted)

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

        Raises
        ------
        - AccountLoginFail: Invalid password provided.
        - AccountDoesNotExist: Invalid email/username.
        - VerificationCodeRateLimited: Too many verification code requests.
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
            status, cookies = await self._check_qrcode(creation_result.ticket)
            if status is QRCodeStatus.SCANNED and not scanned:
                LOGGER_.info("QR code scanned")
                scanned = True
            elif status is QRCodeStatus.CONFIRMED:
                LOGGER_.info("QR code login confirmed")
                break

            await asyncio.sleep(1)

        self.set_cookies(cookies)
        dict_cookies = {key: morsel.value for key, morsel in cookies.items()}
        return QRLoginResult(**dict_cookies)

    @managers.no_multi
    async def create_mmt(self) -> MMT:
        """Create a geetest challenge."""
        if self.default_game is None:
            raise ValueError("No default game set.")

        headers = {
            "DS": ds_utility.generate_geetest_ds(self.region),
            **auth_utility.CREATE_MMT_HEADERS[self.region],
        }

        url = routes.CREATE_MMT_URL.get_url(self.region)
        if self.region is types.Region.OVERSEAS:
            url = url.update_query(app_key=constants.GEETEST_RECORD_KEYS[self.default_game])

        assert isinstance(self.cookie_manager, managers.CookieManager)
        async with self.cookie_manager.create_session() as session:
            async with session.get(url, headers=headers, cookies=self.cookie_manager.cookies) as r:
                data = await r.json()

        if not data["data"]:
            errors.raise_for_retcode(data)

        return MMT(**data["data"])

    @base.region_specific(types.Region.OVERSEAS)
    @managers.no_multi
    async def verify_mmt(self, mmt_result: MMTResult) -> None:
        """Verify a geetest challenge."""
        if self.default_game is None:
            raise ValueError("No default game set.")

        headers = {
            "DS": ds_utility.generate_geetest_ds(self.region),
            **auth_utility.CREATE_MMT_HEADERS[self.region],
        }

        body = mmt_result.model_dump()
        body["app_key"] = constants.GEETEST_RECORD_KEYS[self.default_game]

        assert isinstance(self.cookie_manager, managers.CookieManager)
        async with self.cookie_manager.create_session() as session:
            async with session.post(
                routes.VERIFY_MMT_URL.get_url(), json=body, headers=headers, cookies=self.cookie_manager.cookies
            ) as r:
                data = await r.json()

        if not data["data"]:
            errors.raise_for_retcode(data)

    async def os_game_login(
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = False,
        port: int = 5000,
        geetest_solver: typing.Optional[typing.Callable[[RiskyCheckMMT], typing.Awaitable[RiskyCheckMMTResult]]] = None,
    ) -> GameLoginResult:
        """Perform a login to the game.

        Raises
        ------
        - IncorrectGameAccount: Invalid account provided.
        - IncorrectGamePassword: Invalid password provided.
        """
        api_server = "api.geetest.com" if self.region is types.Region.CHINESE else "api-na.geetest.com"

        result = await self._shield_login(account, password, encrypted=encrypted)

        if isinstance(result, RiskyCheckMMT):
            if geetest_solver:
                mmt_result = await geetest_solver(result)
            else:
                mmt_result = await server.solve_geetest(result, port=port, api_server=api_server)

            result = await self._shield_login(account, password, encrypted=encrypted, mmt_result=mmt_result)

        if not result.device_grant_required:
            return await self._os_game_login(result.account.uid, result.account.token)

        mmt = await self._send_game_verification_email(result.account.device_grant_ticket)
        if mmt:
            if geetest_solver:
                mmt_result = await geetest_solver(mmt)
            else:
                mmt_result = await server.solve_geetest(mmt, port=port, api_server=api_server)

            await self._send_game_verification_email(result.account.device_grant_ticket, mmt_result=mmt_result)

        code = await server.enter_code()
        verification_result = await self._verify_game_email(code, result.account.device_grant_ticket)

        return await self._os_game_login(result.account.uid, verification_result.game_token)

    def _gen_random_fp(self) -> str:
        """Generate a random device fingerprint used for generating authentic device fingerprint."""
        char = digits + "abcdef"
        return "".join(random.choices(char, k=13))

    def _gen_ext_fields(self, oaid: str, board: str) -> str:
        oaid_key = "oaid" if self.region is types.Region.CHINESE else "adid"
        ext_fields = {oaid_key: oaid, "board": board}
        return json.dumps(ext_fields)

    async def generate_fp(
        self,
        *,
        device_id: str,
        device_board: str,
        oaid: str,
    ) -> str:
        """Generate an authentic device fingerprint."""
        device_id_key = "bbs_device_id" if self.region is types.Region.CHINESE else "hoyolab_device_id"
        payload = {
            "device_id": device_id,
            "device_fp": self._gen_random_fp(),
            "seed_id": str(uuid.uuid4()).lower(),
            "seed_time": str(int(time.time() * 1000)),
            "platform": "2",
            "app_name": "bbs_cn" if self.region is types.Region.CHINESE else "bbs_oversea",
            "ext_fields": self._gen_ext_fields(oaid, device_board),
            device_id_key: str(uuid.uuid4()).lower(),
        }

        async with (
            aiohttp.ClientSession() as session,
            session.post(routes.GET_FP_URL.get_url(self.region), json=payload) as r,
        ):
            data = await r.json()

        if data["data"]["code"] != 200:
            raise errors.GenshinException(data, data["data"]["msg"])

        return data["data"]["device_fp"]
