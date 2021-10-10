from typing import List

from pydantic import Field

from .base import GenshinModel, PartialCharacter


class Weapon(GenshinModel):
    id: int
    icon: str
    name: str
    rarity: int
    description: str = Field(alias="desc")
    level: int
    type: str = Field(alias="type_name")
    ascensions: int = Field(alias="promote_level")
    refinement: int = Field(alias="affix_level")


class ArtifactSetEffect(GenshinModel):
    pieces: int = Field(alias="activation_number")
    effect: str


class ArtifactSet(GenshinModel):
    id: int
    name: str
    effects: List[ArtifactSetEffect]


class Artifact(GenshinModel):
    id: int
    icon: str
    name: str
    pos_name: str
    pos: int
    rarity: int


class Constellation(GenshinModel):
    id: int
    icon: str
    pos: int
    name: str
    effect: str
    activated: bool = Field(alias="is_actived")


class Outfit(GenshinModel):
    id: int
    icon: str
    name: str


class Character(PartialCharacter):
    """A character with stats and equipment"""

    weapon: Weapon
    artifacts: List[Artifact] = Field(alias="reliquaries")
    constellations: List[Constellation]
    outfits: List[Outfit] = Field(alias="costumes")
