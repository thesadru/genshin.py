"""Geetest-related models"""

import json
import typing

import pydantic

from genshin.utility import auth as auth_utility

__all__ = [
    "BaseMMT",
    "BaseMMTResult",
    "BaseSessionMMTResult",
    "MMT",
    "MMTResult",
    "MMTv4",
    "MMTv4Result",
    "SessionMMT",
    "SessionMMTResult",
    "SessionMMTv4",
    "SessionMMTv4Result",
]


class BaseMMT(pydantic.BaseModel):
    """Base Geetest verification data model."""

    new_captcha: int
    success: int

    @pydantic.model_validator(mode="before")
    def __parse_data(cls, data: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """Parse the data if it was provided in a raw format."""
        if "data" in data:
            # Assume the data is aigis header and parse it
            session_id = data["session_id"]
            data = data["data"]
            if isinstance(data, str):
                data = json.loads(data)

            data["session_id"] = session_id

        return data


class MMT(BaseMMT):
    """Geetest verification data."""

    challenge: str
    gt: str


class SessionMMT(MMT):
    """Session-based geetest verification data."""

    session_id: str

    def get_mmt(self) -> MMT:
        """Get the base MMT data."""
        return MMT(**self.model_dump(exclude={"session_id"}))


class MMTv4(BaseMMT):
    """Geetest verification data (V4)."""

    captcha_id: str = pydantic.Field(alias="gt")
    risk_type: str


class SessionMMTv4(MMTv4):
    """Session-based geetest verification data (V4)."""

    session_id: str

    def get_mmt(self) -> MMTv4:
        """Get the base MMTv4 data."""
        return MMTv4(**self.model_dump(exclude={"session_id"}))


class BaseMMTResult(pydantic.BaseModel):
    """Base Geetest verification result model."""

    def get_data(self) -> typing.Dict[str, typing.Any]:
        """Get the base MMT result data.

        This method acts as `model_dump` but excludes the `session_id` field.
        """
        return self.model_dump(exclude={"session_id"})


class BaseSessionMMTResult(BaseMMTResult):
    """Base session-based Geetest verification result model."""

    session_id: str

    def to_aigis_header(self) -> str:
        """Convert the result to `x-rpc-aigis` header."""
        return auth_utility.get_aigis_header(self.session_id, self.get_data())


class MMTResult(BaseMMTResult):
    """Geetest verification result."""

    geetest_challenge: str
    geetest_validate: str
    geetest_seccode: str


class SessionMMTResult(MMTResult, BaseSessionMMTResult):
    """Session-based geetest verification result."""


class MMTv4Result(BaseMMTResult):
    """Geetest verification result (V4)."""

    captcha_id: str
    lot_number: str
    pass_token: str
    gen_time: str
    captcha_output: str


class SessionMMTv4Result(MMTv4Result, BaseSessionMMTResult):
    """Session-based geetest verification result (V4)."""
