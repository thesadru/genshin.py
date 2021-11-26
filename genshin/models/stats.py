from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydantic import Field, validator

from .abyss import SpiralAbyssPair
from .activities import Activities
from .base import GenshinModel, PartialCharacter
from .character import Character

__all__ = [
    "Stats",
    "Offering",
    "Exploration",
    "TeapotRealm",
    "Teapot",
    "PartialUserStats",
    "UserStats",
    "FullUserStats",
]

# flake8: noqa: E222
class Stats(GenshinModel):
    """Overall user stats"""

    # This is such fucking bullshit, just why?
    # fmt: off
    achievements: int =       Field(galias="achievement_number",     mi18n="bbs/achievement_complete_count")
    days_active: int =        Field(galias="active_day_number",      mi18n="bbs/active_day")
    characters: int =         Field(galias="avatar_number",          mi18n="bbs/other_people_character")
    spiral_abyss: str =       Field(galias="spiral_abyss",           mi18n="bbs/unlock_portal")
    anemoculi: int =          Field(galias="anemoculus_number",      mi18n="bbs/wind_god")
    geoculi: int =            Field(galias="geoculus_number",        mi18n="bbs/rock_god")
    electroculi: int =        Field(galias="electroculus_number",    mi18n="bbs/electroculus_god")
    common_chests: int =      Field(galias="common_chest_number",    mi18n="bbs/general_treasure_box_count")
    exquisite_chests: int =   Field(galias="exquisite_chest_number", mi18n="bbs/delicacy_treasure_box_count")
    precious_chests: int =    Field(galias="precious_chest_number",  mi18n="bbs/rarity_treasure_box_count")
    luxurious_chests: int =   Field(galias="luxurious_chest_number", mi18n="bbs/magnificent_treasure_box_count")
    remarkable_chests: int =  Field(galias="magic_chest_number",     mi18n="bbs/magic_chest_number")
    unlocked_waypoints: int = Field(galias="way_point_number",       mi18n="bbs/unlock_portal")
    unlocked_domains: int =   Field(galias="domain_number",          mi18n="bbs/unlock_secret_area")
    # fmt: on

    def as_dict(self, lang: str = "en-us") -> Dict[str, Any]:
        """Helper function which turns fields into properly named ones"""
        return {
            self._get_mi18n(field, lang): getattr(self, field.name)
            for field in self.__fields__.values()
        }


class Offering(GenshinModel):
    """An offering"""

    name: str
    level: int


class Exploration(GenshinModel):
    """Exploration data"""

    id: int
    icon: str
    name: str
    type: str
    level: int
    explored: int = Field(galias="exploration_percentage")
    offerings: List[Offering]

    @property
    def percentage(self) -> float:
        """The percentage explored"""
        return self.explored / 10


class TeapotRealm(GenshinModel):
    """A specific teapot realm"""

    name: str
    icon: str

    @property
    def id(self) -> int:
        match = re.search(r"\d", self.icon)
        return int(match.group()) if match else 0


class Teapot(GenshinModel):
    """User's Serenitea Teapot"""

    realms: List[TeapotRealm]
    level: int
    visitors: int = Field(galias="visit_num")
    comfort: int = Field(galias="comfort_num")
    items: int = Field(galias="item_num")
    comfort_name: str = Field(galias="comfort_level_name")
    comfort_icon: str = Field(galias="comfort_level_icon")


class PartialUserStats(GenshinModel):
    """User stats with characters without equipment"""

    stats: Stats
    characters: List[PartialCharacter] = Field(galias="avatars")
    explorations: List[Exploration] = Field(galias="world_explorations")
    teapot: Optional[Teapot] = Field(galias="homes")

    @validator("teapot", pre=True)
    def __format_teapot(cls, v):
        if not v:
            return None
        if isinstance(v, dict):
            return v
        return {**v[0], "realms": v}


class UserStats(PartialUserStats):
    """User stats with characters with equipment"""

    characters: List[Character] = Field(galias="avatars")


class FullUserStats(UserStats):
    """User stats with all data a user can have"""

    abyss: SpiralAbyssPair
    activities: Activities
