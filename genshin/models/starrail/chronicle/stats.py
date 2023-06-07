"""Starrail chronicle stats."""
import typing

from genshin.models.model import Aliased, APIModel
from .. import character

__all__ = [
    "StarRailUserStats",
    "PartialStarRailUserStats",
    "StarRailUserInfo",
    "Stats",
]


class Stats(APIModel):
    """Overall user stats."""

    active_days: int
    avatar_num: int
    achievement_num: int
    chest_num: int
    abyss_process: str


class PartialStarRailUserStats(APIModel):
    """User stats with characters without equipment."""

    stats: Stats
    characters: typing.Sequence[character.PartialCharacter] = Aliased("avatar_list")


class StarRailUserInfo(APIModel):
    """User info."""

    nickname: str
    server: str = Aliased("region")
    level: int
    avatar: str


class StarRailUserStats(PartialStarRailUserStats):
    """User stats"""

    info: StarRailUserInfo
