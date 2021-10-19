from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import Field, validator

from .abyss import SpiralAbyssPair
from .activities import Activities
from .base import GenshinModel, PartialCharacter
from .character import Character

# flake8: noqa: E222
class Stats(GenshinModel):
    """Overall user stats"""

    # This is such fucking bullshit, just why?
    # fmt: off
    achievements: int =       Field(galias="achievement_number")
    days_active: int =        Field(galias="active_day_number")
    characters: int =         Field(galias="avatar_number")
    spiral_abyss: str =       Field(galias="spiral_abyss")
    anemoculi: int =          Field(galias="anemoculus_number")
    geoculi: int =            Field(galias="geoculus_number")
    electroculi: int =        Field(galias="electroculus_number")
    common_chests: int =      Field(galias="common_chest_number")
    exquisite_chests: int =   Field(galias="exquisite_chest_number")
    precious_chests: int =    Field(galias="precious_chest_number")
    luxurious_chests: int =   Field(galias="luxurious_chest_number")
    unlocked_waypoints: int = Field(galias="way_point_number")
    unlocked_domains: int =   Field(galias="domain_number")
    # fmt: on

    def as_dict(self, lang: str = "en-us") -> Dict[str, Any]:
        """Helper function which turns fields into properly named ones"""
        assert lang == "en-us", "Other languages not yet implemented"

        return {key.replace("_", " ").title(): value for key, value in self.dict().items()}


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
