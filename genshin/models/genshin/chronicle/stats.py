from __future__ import annotations

import re
import typing

import pydantic

from genshin.models import hoyolab
from genshin.models.model import Aliased, APIModel

from . import abyss, activities
from . import characters as characters_module

__all__ = [
    "AreaExploration",
    "BossKill",
    "Exploration",
    "FullGenshinUserStats",
    "GenshinUserStats",
    "NatlanReputation",
    "NatlanTribe",
    "Offering",
    "PartialGenshinUserStats",
    "Stats",
    "Teapot",
    "TeapotRealm",
]


class ImgTheaterStats(APIModel):
    """Imaginarium Theater stats."""

    unlocked: bool = Aliased("is_unlock")
    max_act: int = Aliased("max_round_id")
    has_data: bool
    has_detail_data: bool


class StygianOnslaughtStats(APIModel):
    """Stygian Onslaught stats."""

    difficulty: int
    name: str
    has_data: bool
    unlocked: bool = Aliased("is_unlock")


# flake8: noqa: E222
class Stats(APIModel):
    """Overall user stats."""

    achievements: int = Aliased("achievement_number")
    days_active: int = Aliased("active_day_number")
    characters: int = Aliased("avatar_number")
    spiral_abyss: str = Aliased("spiral_abyss")
    anemoculi: int = Aliased("anemoculus_number")
    geoculi: int = Aliased("geoculus_number")
    dendroculi: int = Aliased("dendroculus_number")
    electroculi: int = Aliased("electroculus_number")
    hydroculi: int = Aliased("hydroculus_number")
    pyroculi: int = Aliased("pyroculus_number")
    common_chests: int = Aliased("common_chest_number")
    exquisite_chests: int = Aliased("exquisite_chest_number")
    precious_chests: int = Aliased("precious_chest_number")
    luxurious_chests: int = Aliased("luxurious_chest_number")
    remarkable_chests: int = Aliased("magic_chest_number")
    unlocked_waypoints: int = Aliased("way_point_number")
    unlocked_domains: int = Aliased("domain_number")
    max_friendship_characters: int = Aliased("full_fetter_avatar_num")

    theater: ImgTheaterStats = Aliased("role_combat")
    stygian: StygianOnslaughtStats = Aliased("hard_challenge")


class Offering(APIModel):
    """Exploration offering."""

    name: str
    level: int
    icon: str = ""


class BossKill(APIModel):
    """Boss kills in exploration"""

    name: str
    kills: int = Aliased("kill_num")


class AreaExploration(APIModel):
    """Area exploration data."""

    name: str
    raw_explored: int = Aliased("exploration_percentage")

    @property
    def explored(self) -> float:
        """The percentage explored. (Note: This can go above 100%)"""
        return self.raw_explored / 10


class NatlanTribe(APIModel):
    """Natlan tribe data."""

    icon: str
    image: str
    name: str
    id: int
    level: int


class NatlanReputation(APIModel):
    """Natlan reputation data."""

    tribes: typing.Sequence[NatlanTribe] = Aliased("tribal_list")


class Exploration(APIModel):
    """Exploration data."""

    id: int
    parent_id: int
    name: str
    raw_explored: int = Aliased("exploration_percentage")

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
    natlan_reputation: typing.Optional[NatlanReputation] = Aliased("natan_reputation", default=None)

    @property
    def explored(self) -> float:
        """The percentage explored."""
        return self.raw_explored / 10

    @pydantic.field_validator("offerings", mode="before")
    def __add_base_offering(
        cls, offerings: typing.Sequence[typing.Any], info: pydantic.ValidationInfo
    ) -> typing.Sequence[typing.Any]:
        if info.data["type"] == "Reputation" and not any(info.data["type"] == o["name"] for o in offerings):
            offerings = [*offerings, dict(name=info.data["type"], level=info.data["level"])]

        return offerings


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
    visitors: int = Aliased("visit_num")
    comfort: int = Aliased("comfort_num")
    items: int = Aliased("item_num")
    comfort_name: str = Aliased("comfort_level_name")
    comfort_icon: str = Aliased("comfort_level_icon")


class PartialGenshinUserStats(APIModel):
    """User stats with characters without equipment."""

    info: hoyolab.UserInfo = Aliased("role")
    stats: Stats
    characters: typing.Sequence[characters_module.PartialCharacter] = Aliased("avatars")
    explorations: typing.Sequence[Exploration] = Aliased("world_explorations")
    teapot: typing.Optional[Teapot] = Aliased("homes")

    @pydantic.field_validator("teapot", mode="before")
    def __format_teapot(cls, v: typing.Any) -> typing.Optional[dict[str, typing.Any]]:
        if not v:
            return None
        if isinstance(v, dict):
            return typing.cast("dict[str, typing.Any]", v)
        return {**v[0], "realms": v}

    @pydantic.field_validator("characters", mode="before")
    def __format_characters(cls, v: typing.Sequence[typing.Any]) -> typing.Sequence[typing.Any]:
        return [c for c in v if c["id"] != 0]


class GenshinUserStats(PartialGenshinUserStats):
    """User stats with characters with equipment"""

    characters: typing.Sequence[characters_module.Character] = Aliased("list")


class FullGenshinUserStats(GenshinUserStats):
    """User stats with all data a user can have"""

    abyss: abyss.SpiralAbyssPair
    activities: activities.Activities
