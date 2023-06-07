from genshin.models.model import APIModel, Unique


class BaseCharacter(APIModel, Unique):
    """Base character model."""

    id: int
    name: str
    element: str
    rarity: int
    icon: str


class PartialCharacter(BaseCharacter):
    """Character without any equipment."""

    level: int
    rank: int
