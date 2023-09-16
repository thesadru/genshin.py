"""Starrail base character model."""
from genshin.models.model import APIModel, Unique


class StarRailBaseCharacter(APIModel, Unique):
    """Base character model."""

    id: int
    element: str
    rarity: int
    icon: str


class StarRailPartialCharacter(StarRailBaseCharacter):
    """Character without any equipment."""

    name: str
    level: int
    rank: int


class FloorCharacter(StarRailBaseCharacter):
    """Character in a floor."""

    level: int
    rank: int


class RogueCharacter(StarRailBaseCharacter):
    """Rogue character model."""

    level: int
    rank: int
