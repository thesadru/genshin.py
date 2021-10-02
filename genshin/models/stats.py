from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field, validator

from .base import Character
from .character import EquippedCharacter


class Stats(BaseModel):
    # This is such fucking bullshit, just why?
    # fmt: off
    achievements: int =       Field(alias="achievement_number")
    active_days: int =        Field(alias="active_day_number")
    characters: int =         Field(alias="avatar_number")
    spiral_abyss: str =       Field(alias="spiral_abyss")
    anemoculi: int =          Field(alias="anemoculus_number")
    geoculi: int =            Field(alias="geoculus_number")
    electroculi: int =        Field(alias="electroculus_number")
    common_chests: int =      Field(alias="common_chest_number")
    exquisite_chests: int =   Field(alias="exquisite_chest_number")
    precious_chests: int =    Field(alias="precious_chest_number")
    luxurious_chests: int =   Field(alias="luxurious_chest_number")
    unlocked_waypoints: int = Field(alias="way_point_number")
    unlocked_domains: int =   Field(alias="domain_number")
    # fmt: on


class Offering(BaseModel):
    name: str
    level: int


class Exploration(BaseModel):
    level: int
    _explored = Field(alias="exploration_percentage")
    icon: str
    name: str
    type: str
    offerings: List[Offering]
    id: int


class TeapotRealm(BaseModel):
    name: str
    icon: str


class Teapot(BaseModel):
    realms: List[TeapotRealm]
    level: int
    visitors: int = Field(alias="visit_num")
    comfort: int = Field(alias="comfort_num")
    items: int = Field(alias="item_num")
    comfort_name: str = Field(alias="comfort_level_name")
    comfort_icon: str = Field(alias="comfort_level_icon")


class PartialUserStats(BaseModel):
    partial: Literal[True] = True
    
    stats: Stats
    characters: List[Character] = Field(alias="avatars")
    explorations: List[Exploration] = Field(alias="world_explorations")
    teapot: Teapot = Field(alias="homes")

    @validator("teapot", pre=True)
    def __format_teapot(cls, v):
        if isinstance(v, dict):
            return v
        value = v[0]
        value["realms"] = v
        return value

class UserStats(PartialUserStats):
    """User stats with characters with equipment"""
    partial: Literal[False] = False

    characters: List[EquippedCharacter] = Field(alias="avatars")
