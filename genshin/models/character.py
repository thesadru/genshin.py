from enum import Enum
from typing import List

from pydantic import BaseModel, Field, HttpUrl

from .stats import BaseCharacter


class WeaponType(str, Enum):
    sword = "Sword"
    polearm = "Polearm"
    claymore = "Claymore"
    catalyst = "Catalyst"
    bow = "Bow"

    def __str__(self) -> str:
        return self.name


class Weapon(BaseModel):
    id: int
    icon: HttpUrl
    name: str
    rarity: int
    description: str = Field(alias="desc")
    level: int
    type: WeaponType = Field(alias="type_name")
    ascensions: int = Field(alias="promote_level")
    refinement: int = Field(alias="affix_level")


class ArtifactSetEffect(BaseModel):
    pieces: int = Field(alias="activation_number")
    effect: str


class ArtifactSet(BaseModel):
    id: int
    name: str
    effects: List[ArtifactSetEffect]


class Artifact(BaseModel):
    id: int
    icon: HttpUrl
    name: str
    pos_name: str
    pos: int
    rarity: int


class Constellation(BaseModel):
    id: int
    icon: HttpUrl
    pos: int
    name: str
    effect: str
    activated: bool = Field(alias="is_actived")


class Outfit(BaseModel):
    id: int
    icon: HttpUrl
    name: str


class Character(BaseCharacter):
    """A character but with equipment"""

    weapon: Weapon
    artifacts: List[Artifact] = Field(alias="reliquaries")
    constellations: List[Constellation]
    outfits: List[Outfit] = Field(alias="costumes")
