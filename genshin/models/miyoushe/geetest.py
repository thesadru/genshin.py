"""Miyoushe Geetest Models"""

from pydantic import BaseModel

__all__ = ("MiyousheGeetest",)


class MiyousheGeetest(BaseModel):
    """Stoken result."""

    challenge: str
    gt: str
    new_captcha: int
    success: int
