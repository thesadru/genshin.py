"""Cookie-related models"""

import typing

import pydantic

__all__ = [
    "AppLoginResult",
    "QRLoginResult",
    "StokenResult",
    "WebLoginResult",
]


class StokenResult(pydantic.BaseModel):
    """Result of fetching `stoken` with `fetch_stoken_by_game_token`."""

    aid: str
    mid: str
    token: str

    @pydantic.model_validator(mode="before")
    def _transform_result(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        return {
            "aid": values["user_info"]["aid"],
            "mid": values["user_info"]["mid"],
            "token": values["token"]["token"],
        }


class QRLoginResult(pydantic.BaseModel):
    """QR code login cookies.

    Returned by `client.login_with_qrcode`.
    """

    stoken: str
    stuid: str
    mid: str
    cookie_token: str


class AppLoginResult(pydantic.BaseModel):
    """App login cookies.

    Returned by `client.login_with_app_password`.
    """

    stoken: str
    ltuid_v2: str
    ltmid_v2: str
    account_id_v2: str
    account_mid_v2: str


class WebLoginResult(pydantic.BaseModel):
    """Web login cookies.

    Returned by `client.login_with_password`.
    """

    cookie_token_v2: str
    account_mid_v2: str
    account_id_v2: str
    ltoken_v2: str
    ltmid_v2: str
    ltuid_v2: str
