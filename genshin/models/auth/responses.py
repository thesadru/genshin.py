"""Auth endpoints responses models."""

import typing

import pydantic

__all__ = ["Account", "ShieldLoginResponse"]


class Account(pydantic.BaseModel):
    """Account data returned by the shield login endpoint."""

    uid: str
    name: str
    email: str
    mobile: str
    is_email_verify: str
    realname: str
    identity_card: str
    token: str
    safe_mobile: str
    facebook_name: str
    google_name: str
    twitter_name: str
    game_center_name: str
    apple_name: str
    sony_name: str
    tap_name: str
    country: str
    reactivate_ticket: str
    area_code: str
    device_grant_ticket: str
    steam_name: str
    unmasked_email: str
    unmasked_email_type: int
    cx_name: typing.Optional[str] = None


class ShieldLoginResponse(pydantic.BaseModel):
    """Response model for the shield login endpoint."""

    account: Account
    device_grant_required: bool
    safe_moblie_required: bool
    realperson_required: bool
    reactivate_required: bool
    realname_operation: str
