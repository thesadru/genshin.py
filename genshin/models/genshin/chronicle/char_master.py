from enum import IntEnum

import pydantic

__all__ = ("EnvisagedEchoCharacter", "EnvisagedEchoStatus")


class EnvisagedEchoStatus(IntEnum):
    """Status of an Envisaged Echo character."""

    LOCKED = 1
    UNLOCKED = 2
    CHECKED = 3
    """With a green checkmark icon."""


class EnvisagedEchoCharacter(pydantic.BaseModel):
    """Genshin Impact Envisaged Echo character."""

    id: int = pydantic.Field(alias="avatar_id")
    name: str
    icon: str
    status: EnvisagedEchoStatus
    has_red_dot: bool
    level_id: int
