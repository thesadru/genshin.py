from typing import Dict, List

from pydantic import Field, validator

from .base import GenshinModel, PartialCharacter, Unique

__all__ = [
    "PartialCharacter",
    "Weapon",
    "ArtifactSetEffect",
    "ArtifactSet",
    "Artifact",
    "Constellation",
    "Outfit",
    "Character",
]


class Weapon(GenshinModel, Unique):
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
    enabled: bool = False

    class Config:
        # this is for the "enabled" field, hopefully nobody abuses this
        allow_mutation = True


class ArtifactSet(GenshinModel, Unique):
    """An artifact set"""

    id: int
    name: str
    effects: List[ArtifactSetEffect] = Field(galias="affixes")


class Artifact(GenshinModel, Unique):
    """A character's equipped artifact"""

    id: int
    icon: str
    name: str
    pos_name: str
    pos: int
    rarity: int
    level: int
    set: ArtifactSet


class Constellation(GenshinModel, Unique):
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


class Outfit(GenshinModel, Unique):
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

    @validator("artifacts")
    def __add_artifact_effect_enabled(cls, artifacts: List[Artifact]):
        sets: Dict[int, List[Artifact]] = {}
        for arti in artifacts:
            sets.setdefault(arti.set.id, []).append(arti)

        for artifact in artifacts:
            for effect in artifact.set.effects:
                if effect.pieces <= len(sets[artifact.set.id]):
                    effect.enabled = True

        return artifacts
