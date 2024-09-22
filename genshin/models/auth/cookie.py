"""Cookie-related models"""

import typing

import pydantic

__all__ = [
    "AppLoginResult",
    "CNWebLoginResult",
    "CookieLoginResult",
    "DeviceGrantResult",
    "DeviceGrantResult",
    "GameLoginResult",
    "MobileLoginResult",
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
    def _transform_result(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        return {
            "aid": values["user_info"]["aid"],
            "mid": values["user_info"]["mid"],
            "token": values["token"]["token"],
        }


class CookieLoginResult(pydantic.BaseModel):
    """Base model for cookie login result."""

    def to_str(self) -> str:
        """Convert the login cookies to a string."""
        return "; ".join(f"{key}={value}" for key, value in self.model_dump().items())

    def to_dict(self) -> dict[str, str]:
        """Convert the login cookies to a dictionary."""
        return self.model_dump()


class QRLoginResult(CookieLoginResult):
    """QR code login cookies.

    Returned by `client.login_with_qrcode`.
    """

    cookie_token_v2: str
    account_mid_v2: str
    account_id_v2: str
    ltoken_v2: str
    ltmid_v2: str
    ltuid_v2: str


class AppLoginResult(CookieLoginResult):
    """App login cookies.

    Returned by `client.login_with_app_password`.
    """

    stoken: str
    ltuid_v2: str
    ltmid_v2: str
    account_id_v2: str
    account_mid_v2: str


class WebLoginResult(CookieLoginResult):
    """Web login cookies.

    Returned by `client.login_with_password`.
    """

    cookie_token_v2: str
    account_mid_v2: str
    account_id_v2: str
    ltoken_v2: str
    ltmid_v2: str
    ltuid_v2: str


class CNWebLoginResult(CookieLoginResult):
    """Web login cookies.

    Returned by `client.cn_login_with_password`.
    """

    cookie_token_v2: str
    account_mid_v2: str
    account_id_v2: str
    ltoken_v2: str
    ltmid_v2: str
    ltuid_v2: str


class MobileLoginResult(CookieLoginResult):
    """Mobile number login cookies.

    Returned by `client.login_with_mobile_number`.
    """

    cookie_token_v2: str
    account_mid_v2: str
    account_id_v2: str
    ltoken_v2: str
    ltmid_v2: str


class DeviceGrantResult(pydantic.BaseModel):
    """Cookies returned by the device grant endpoint."""

    game_token: str
    login_ticket: typing.Optional[str] = None

    @pydantic.model_validator(mode="before")
    def _str_to_none(cls, data: dict[str, typing.Union[str, None]]) -> dict[str, typing.Union[str, None]]:
        """Convert empty strings to `None`."""
        for key in data:
            if data[key] == "" or data[key] == "None":
                data[key] = None
        return data


class GameLoginResult(pydantic.BaseModel):
    """Game login result."""

    combo_id: str
    open_id: str
    combo_token: str
    heartbeat: bool
    account_type: int
