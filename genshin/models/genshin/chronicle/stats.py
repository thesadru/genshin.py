from __future__ import annotations

import re
import typing

import pydantic

from genshin.models import hoyolab
from genshin.models.model import APIModel

from . import abyss
from . import characters as character_models

__all__ = [
    "AreaExploration",
    "BossKill",
    "Exploration",
    "FullGenshinUserStats",
    "GenshinUserStats",
    "Offering",
    "PartialGenshinUserStats",
    "Stats",
    "Teapot",
    "TeapotRealm",
]


# flake8: noqa: E222
class Stats(APIModel):
    """Overall user stats."""

    # This is such fucking bullshit, just why?

    achievements: int = pydantic.Field(alias="achievement_number")
    days_active: int = pydantic.Field(alias="active_day_number")
    characters: int = pydantic.Field(alias="avatar_number")
    spiral_abyss: str = pydantic.Field(alias="spiral_abyss")
    anemoculi: int = pydantic.Field(alias="anemoculus_number")
    geoculi: int = pydantic.Field(alias="geoculus_number")
    dendroculi: int = pydantic.Field(alias="dendroculus_number")
    electroculi: int = pydantic.Field(alias="electroculus_number")
    hydroculi: int = pydantic.Field(alias="hydroculus_number")
    common_chests: int = pydantic.Field(alias="common_chest_number")
    exquisite_chests: int = pydantic.Field(alias="exquisite_chest_number")
    precious_chests: int = pydantic.Field(alias="precious_chest_number")
    luxurious_chests: int = pydantic.Field(alias="luxurious_chest_number")
    remarkable_chests: int = pydantic.Field(alias="magic_chest_number")
    unlocked_waypoints: int = pydantic.Field(alias="way_point_number")
    unlocked_domains: int = pydantic.Field(alias="domain_number")


class Offering(APIModel):
    """Exploration offering."""

    name: str
    level: int
    icon: str = ""


class BossKill(APIModel):
    """Boss kills in exploration"""

    name: str
    kills: int = pydantic.Field(alias="kill_num")


class AreaExploration(APIModel):
    """Area exploration data."""

    name: str
    raw_explored: int = pydantic.Field(alias="exploration_percentage")

    @property
    def explored(self) -> float:
        """The percentage explored. (Note: This can go above 100%)"""
        return self.raw_explored / 10


class Exploration(APIModel):
    """Exploration data."""

    id: int
    parent_id: int
    name: str
    raw_explored: int = pydantic.Field(alias="exploration_percentage")

    # deprecated in a sense:
    type: str
    level: int

    icon: str
    inner_icon: str
    background_image: str
    cover: str
    map_url: str

    offerings: typing.Sequence[Offering]
    boss_list: typing.Sequence[BossKill]
    area_exploration_list: typing.Sequence[AreaExploration]

    @property
    def explored(self) -> float:
        """The percentage explored."""
        return self.raw_explored / 10


class TeapotRealm(APIModel):
    """A specific teapot realm."""

    name: str
    icon: str

    @property
    def id(self) -> int:
        match = re.search(r"\d", self.icon)
        return int(match.group()) if match else 0


class Teapot(APIModel):
    """User's Serenitea Teapot."""

    realms: typing.Sequence[TeapotRealm]
    level: int
    visitors: int = pydantic.Field(alias="visit_num")
    comfort: int = pydantic.Field(alias="comfort_num")
    items: int = pydantic.Field(alias="item_num")
    comfort_name: str = pydantic.Field(alias="comfort_level_name")
    comfort_icon: str = pydantic.Field(alias="comfort_level_icon")


class PartialGenshinUserStats(APIModel):
    """User stats with characters without equipment."""

    info: hoyolab.UserInfo = pydantic.Field(alias="role")
    stats: Stats
    characters: typing.Sequence[character_models.PartialCharacter] = pydantic.Field(alias="avatars")
    explorations: typing.Sequence[Exploration] = pydantic.Field(alias="world_explorations")
    teapot: typing.Optional[Teapot] = pydantic.Field(alias="homes")

    @pydantic.field_validator("teapot", mode="before")
    @classmethod
    def __format_teapot(cls, v: typing.Any) -> typing.Optional[typing.Dict[str, typing.Any]]:
        if not v:
            return None
        if isinstance(v, dict):
            return typing.cast("dict[str, typing.Any]", v)
        return {**v[0], "realms": v}


class GenshinUserStats(PartialGenshinUserStats):
    """User stats with characters with equipment"""

    characters: typing.Sequence[character_models.Character] = pydantic.Field(alias="avatars")


class FullGenshinUserStats(GenshinUserStats):
    """User stats with all data a user can have"""

    abyss: abyss.SpiralAbyssPair
    activities: typing.Any
