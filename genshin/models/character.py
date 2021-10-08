from typing import List

from pydantic import BaseModel, Field

from .base import PartialCharacter


class Weapon(BaseModel):
    id: int
    icon: str
    name: str
    rarity: int
    description: str = Field(alias="desc")
    level: int
    type: str = Field(alias="type_name")
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
    icon: str
    name: str
    pos_name: str
    pos: int
    rarity: int


class Constellation(BaseModel):
    id: int
    icon: str
    pos: int
    name: str
    effect: str
    activated: bool = Field(alias="is_actived")


class Outfit(BaseModel):
    id: int
    icon: str
    name: str


class Character(PartialCharacter):
    """A character with stats and equipment"""

    weapon: Weapon
    artifacts: List[Artifact] = Field(alias="reliquaries")
    constellations: List[Constellation]
    outfits: List[Outfit] = Field(alias="costumes")
