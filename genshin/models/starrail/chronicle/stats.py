"""Starrail chronicle stats."""
import typing

from genshin.models.model import Aliased, APIModel

from .. import character

__all__ = [
    "PartialStarRailUserStats",
    "StarRailUserInfo",
    "StarRailUserStats",
    "StarRailStats",
]


class StarRailStats(APIModel):
    """Overall user stats."""

    active_days: int
    avatar_num: int
    achievement_num: int
    chest_num: int
    abyss_process: str


class PartialStarRailUserStats(APIModel):
    """User stats with characters without equipment."""

    stats: StarRailStats
    characters: typing.Sequence[character.StarRailPartialCharacter] = Aliased("avatar_list")


class StarRailUserInfo(APIModel):
    """User info."""

    nickname: str
    server: str = Aliased("region")
    level: int
    avatar: str


class StarRailUserStats(PartialStarRailUserStats):
    """User stats."""

    info: StarRailUserInfo
