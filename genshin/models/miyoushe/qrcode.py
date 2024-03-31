"""Miyoushe QR Code Models"""

import json
from enum import Enum

from pydantic import BaseModel, Field, field_validator

__all__ = ("QRCodeCheckResult", "QRCodeCreationResult", "QRCodePayload", "QRCodeRawData", "QRCodeStatus")


class QRCodeStatus(Enum):
    """QR code check status."""

    INIT = "Init"
    SCANNED = "Scanned"
    CONFIRMED = "Confirmed"


class QRCodeRawData(BaseModel):
    """QR code raw data."""

    account_id: str = Field(alias="uid")
    """Miyoushe account id."""
    game_token: str = Field(alias="token")


class QRCodePayload(BaseModel):
    """QR code check result payload."""

    proto: str
    raw: QRCodeRawData | None
    ext: str

    @field_validator("raw", mode="before")
    def _convert_raw_data(cls, value: str | None) -> QRCodeRawData | None:
        if value:
            return QRCodeRawData(**json.loads(value))
        return None


class QRCodeCheckResult(BaseModel):
    """QR code check result."""

    status: QRCodeStatus = Field(alias="stat")
    payload: QRCodePayload


class QRCodeCreationResult(BaseModel):
    """QR code creation result."""

    app_id: str
    ticket: str
    device_id: str
    url: str
