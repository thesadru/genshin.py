"""Starrail chronicle stats."""

import typing

from genshin.models.model import Aliased, APIModel

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
    dreamscape_pass_sticker: int = Aliased("dream_paster_num")


class PartialStarRailUserStats(APIModel):
    """User stats with characters without equipment."""

    stats: StarRailStats
    characters: typing.Sequence[character.StarRailPartialCharacter] = Aliased("avatar_list")
    in_game_avatar: str = Aliased("cur_head_icon_url")
    phone_background: str = Aliased("phone_background_image_url")


class StarRailUserInfo(APIModel):
    """User info."""

    nickname: str
    server: str = Aliased("region")
    level: int
    avatar: str


class StarRailUserStats(PartialStarRailUserStats):
    """User stats."""

    info: StarRailUserInfo
