"""Miyoushe Cookie Models"""

import typing

from pydantic import BaseModel, model_validator

__all__ = ("StokenResult",)


class StokenResult(BaseModel):
    """Stoken result."""

    aid: str
    mid: str
    token: str

    @model_validator(mode="before")
    def _transform_result(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        return {
            "aid": values["user_info"]["aid"],
            "mid": values["user_info"]["mid"],
            "token": values["token"]["token"],
        }
