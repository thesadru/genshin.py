"""Starrail chronicle stats."""

import typing

import pydantic

from genshin.models.model import APIModel

from .. import character

__all__ = [
    "PartialStarRailUserStats",
    "StarRailStats",
    "StarRailUserInfo",
    "StarRailUserStats",
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
    characters: typing.Sequence[character.StarRailPartialCharacter] = pydantic.Field(alias="avatar_list")


class StarRailUserInfo(APIModel):
    """User info."""

    nickname: str
    server: str = pydantic.Field(alias="region")
    level: int
    avatar: str


class StarRailUserStats(PartialStarRailUserStats):
    """User stats."""

    info: StarRailUserInfo
