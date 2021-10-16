from typing import List

from pydantic import Field

from .base import GenshinModel, PartialCharacter


class Weapon(GenshinModel):
    """A character's equipped weapon"""

    id: int
    icon: str
    name: str
    rarity: int
    description: str = Field(galias="desc")
    level: int
    type: str = Field(galias="type_name")
    ascension: int = Field(galias="promote_level")
    refinement: int = Field(galias="affix_level")


class ArtifactSetEffect(GenshinModel):
    """An effect of an artifact set"""

    pieces: int = Field(galias="activation_number")
    effect: str


class ArtifactSet(GenshinModel):
    """An artifact set"""

    id: int
    name: str
    effects: List[ArtifactSetEffect] = Field(galias="affixes")


class Artifact(GenshinModel):
    """A character's equipped artifact"""

    id: int
    icon: str
    name: str
    pos_name: str
    pos: int
    rarity: int
    set: ArtifactSet


class Constellation(GenshinModel):
    """A character constellation"""

    id: int
    icon: str
    pos: int
    name: str
    effect: str
    activated: bool = Field(galias="is_actived")

    @property
    def scaling(self) -> bool:
        """Whether the constellation is simply for talent scaling"""
        return "U" in self.icon


class Outfit(GenshinModel):
    """An unlocked outfit of a character"""

    id: int
    icon: str
    name: str


class Character(PartialCharacter):
    """A character with equipment"""

    weapon: Weapon
    artifacts: List[Artifact] = Field(galias="reliquaries")
    constellations: List[Constellation]
    outfits: List[Outfit] = Field(galias="costumes")
