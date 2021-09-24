from typing import Any, Dict, List
from pydantic import BaseModel, Field, validator, root_validator, HttpUrl


class BaseCharacter(BaseModel):
    id: int
    image: HttpUrl
    name: str
    element: str
    friendship: int = Field(alias="fetter")
    level: int
    rarity: int
    constellation: int = Field(0, alias="activated_constellation_num")

    collab: bool = False

    @root_validator
    def is_collab(cls, values: Dict[str, Any]):
        if values["rarity"] > 100:
            values["rarity"] -= 100
            values["collab"] = True
        return values


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
    icon: HttpUrl
    name: str
    type: str
    offerings: List[Offering]
    id: int


class TeapotRealm(BaseModel):
    name: str
    icon: HttpUrl


class Teapot(BaseModel):
    realms: List[TeapotRealm]
    level: int
    visitors: int = Field(alias="visit_num")
    comfort: int = Field(alias="comfort_num")
    items: int = Field(alias="item_num")
    comfort_name: str = Field(alias="comfort_level_name")
    comfort_icon: HttpUrl = Field(alias="comfort_level_icon")


class UserStats(BaseModel):
    stats: Stats
    characters: List[BaseCharacter] = Field(alias="avatars")
    explorations: List[Exploration] = Field(alias="world_explorations")
    # teapots: List[Teapot] = Field(alias="homes")  # TODO: Use a single model with lists of names
    teapot: Teapot = Field(alias="homes")

    @validator("teapot", pre=True)
    def format_teapot(cls, v: List[Dict[str, Any]]):
        value = v[0]
        value["realms"] = v
        return value
