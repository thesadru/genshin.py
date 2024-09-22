"""Email verification -related models"""

import json
import typing

import pydantic

__all__ = [
    "ActionTicket",
    "VerifyStrategy",
]


class VerifyStrategy(pydantic.BaseModel):
    """Verification strategy."""

    ticket: str
    verify_type: str


class ActionTicket(pydantic.BaseModel):
    """Action ticket. Can be used to verify email addresses."""

    risk_ticket: str
    verify_str: VerifyStrategy

    @pydantic.model_validator(mode="before")
    def __parse_data(cls, data: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Parse the data if it was provided in a raw format."""
        verify_str = data["verify_str"]
        if isinstance(verify_str, str):
            data["verify_str"] = json.loads(verify_str)

        return data

    def to_rpc_verify_header(self) -> str:
        """Convert the action ticket to `x-rpc-verify` header."""
        ticket = self.model_dump()
        ticket["verify_str"] = json.dumps(ticket["verify_str"])
        return json.dumps(ticket)
