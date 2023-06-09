"""Starrail chronicle character."""
from typing import List, Optional

from genshin.models.model import APIModel

from .. import character

__all__ = [
    "Rank",
    "Relic",
    "StarRailDetailCharacter",
    "StarRailDetailCharacters",
    "StarRailEquipment",
]


class StarRailEquipment(APIModel):
    """Character equipment."""

    id: int
    level: int
    rank: int
    name: str
    desc: str
    icon: str


class Relic(APIModel):
    """Character relic."""

    id: int
    level: int
    pos: int
    name: str
    desc: str
    icon: str
    rarity: int


class Rank(APIModel):
    """Character rank."""

    id: int
    pos: int
    name: str
    icon: str
    desc: str
    is_unlocked: bool


class StarRailDetailCharacter(character.StarRailPartialCharacter):
    """StarRail character with equipment and relics."""

    image: str
    equip: Optional[StarRailEquipment]
    relics: List[Relic]
    ornaments: List[Relic]
    ranks: List[Rank]


class StarRailDetailCharacters(APIModel):
    """StarRail characters."""

    avatar_list: List[StarRailDetailCharacter]
