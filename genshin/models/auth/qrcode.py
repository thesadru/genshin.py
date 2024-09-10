"""Miyoushe QR Code Models"""

import enum
import typing

if typing.TYPE_CHECKING:
    import pydantic.v1 as pydantic
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
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
