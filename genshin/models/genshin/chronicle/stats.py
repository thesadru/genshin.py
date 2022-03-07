from __future__ import annotations

import re
import typing

from pydantic import validator

from genshin.models.model import Aliased, APIModel

from . import characters

__all__ = [
    "Stats",
    "Offering",
    "Exploration",
    "TeapotRealm",
    "Teapot",
    "GenshinPartialUserStats",
]

# flake8: noqa: E222
class Stats(APIModel):
    """Overall user stats."""

    # This is such fucking bullshit, just why?
    # fmt: off
    achievements: int =       Aliased("achievement_number",     mi18n="bbs/achievement_complete_count")
    days_active: int =        Aliased("active_day_number",      mi18n="bbs/active_day")
    characters: int =         Aliased("avatar_number",          mi18n="bbs/other_people_character")
    spiral_abyss: str =       Aliased("spiral_abyss",           mi18n="bbs/unlock_portal")
    anemoculi: int =          Aliased("anemoculus_number",      mi18n="bbs/wind_god")
    geoculi: int =            Aliased("geoculus_number",        mi18n="bbs/rock_god")
    electroculi: int =        Aliased("electroculus_number",    mi18n="bbs/electroculus_god")
    common_chests: int =      Aliased("common_chest_number",    mi18n="bbs/general_treasure_box_count")
    exquisite_chests: int =   Aliased("exquisite_chest_number", mi18n="bbs/delicacy_treasure_box_count")
    precious_chests: int =    Aliased("precious_chest_number",  mi18n="bbs/rarity_treasure_box_count")
    luxurious_chests: int =   Aliased("luxurious_chest_number", mi18n="bbs/magnificent_treasure_box_count")
    remarkable_chests: int =  Aliased("magic_chest_number",     mi18n="bbs/magic_chest_number")
    unlocked_waypoints: int = Aliased("way_point_number",       mi18n="bbs/unlock_portal")
    unlocked_domains: int =   Aliased("domain_number",          mi18n="bbs/unlock_secret_area")
    # fmt: on


class Offering(APIModel):
    """Exploration offering."""

    name: str
    level: int


class Exploration(APIModel):
    """Exploration data."""

    id: int
    icon: str
    name: str
    type: str
    level: int
    explored: int = Aliased("exploration_percentage")
    offerings: typing.Sequence[Offering]

    @property
    def percentage(self) -> float:
        """The percentage explored"""
        return self.explored / 10


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


class GenshinPartialUserStats(APIModel):
    """User stats with characters without equipment."""

    stats: Stats
    characters: typing.Sequence[characters.PartialCharacter] = Aliased("avatars")
    explorations: typing.Sequence[Exploration] = Aliased("world_explorations")
    teapot: typing.Optional[Teapot] = Aliased("homes")

    @validator("teapot", pre=True)
    def __format_teapot(cls, v: typing.Any) -> typing.Optional[typing.Dict[str, typing.Any]]:
        if not v:
            return None
        if isinstance(v, dict):
            return typing.cast("dict[str, typing.Any]", v)
        return {**v[0], "realms": v}
