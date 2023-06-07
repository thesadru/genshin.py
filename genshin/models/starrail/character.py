from genshin.models.model import APIModel, Unique


class BaseCharacter(APIModel, Unique):
    """Base character model."""

    id: int
    element: str
    rarity: int
    icon: str


class PartialCharacter(BaseCharacter):
    """Character without any equipment."""

    name: str
    level: int
    rank: int


class FloorCharacter(BaseCharacter):
    """Character in a floor."""

    level: int


class RogueCharacter(BaseCharacter):
    """Rogue character model."""

    level: int
