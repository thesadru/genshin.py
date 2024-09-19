"""Miyoushe QR Code Models"""

import enum

import pydantic

__all__ = ["QRCodeCreationResult", "QRCodeStatus"]


class QRCodeStatus(enum.Enum):
    """QR code check status."""

    CREATED = "Created"
    SCANNED = "Scanned"
    CONFIRMED = "Confirmed"


class QRCodeCreationResult(pydantic.BaseModel):
    """QR code creation result."""

    ticket: str
    url: str
