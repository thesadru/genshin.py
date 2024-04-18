"""Miyoushe QR Code Models"""

import enum
import json
import typing

import pydantic

__all__ = ["QRCodeCheckResult", "QRCodeCreationResult", "QRCodePayload", "QRCodeRawData", "QRCodeStatus"]


class QRCodeStatus(enum.Enum):
    """QR code check status."""

    INIT = "Init"
    SCANNED = "Scanned"
    CONFIRMED = "Confirmed"


class QRCodeRawData(pydantic.BaseModel):
    """QR code raw data."""

    account_id: str = pydantic.Field(alias="uid")
    """Miyoushe account id."""
    game_token: str = pydantic.Field(alias="token")


class QRCodePayload(pydantic.BaseModel):
    """QR code check result payload."""

    proto: str
    ext: str
    raw: typing.Optional[QRCodeRawData] = None

    @pydantic.field_validator("raw", mode="before")
    def _convert_raw_data(cls, value: typing.Optional[str] = None) -> typing.Union[QRCodeRawData, None]:
        if value:
            return QRCodeRawData(**json.loads(value))
        return None


class QRCodeCheckResult(pydantic.BaseModel):
    """QR code check result."""

    status: QRCodeStatus = pydantic.Field(alias="stat")
    payload: QRCodePayload


class QRCodeCreationResult(pydantic.BaseModel):
    """QR code creation result."""

    app_id: str
    ticket: str
    device_id: str
    url: str