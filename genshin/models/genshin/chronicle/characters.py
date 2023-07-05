"""Genshin chronicle character."""

import typing

if typing.TYPE_CHECKING:
    import pydantic.v1 as pydantic
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
        import pydantic

from genshin.models.genshin import character
from genshin.models.model import Aliased, APIModel, Unique

__all__ = [
    "Artifact",
    "ArtifactSet",
    "ArtifactSetEffect",
    "Character",
    "CharacterWeapon",
    "Constellation",
    "Outfit",
    "PartialCharacter",
]


class PartialCharacter(character.BaseCharacter):
    """Character without any equipment."""

    level: int
    friendship: int = Aliased("fetter")
    constellation: int = Aliased("actived_constellation_num")


class CharacterWeapon(APIModel, Unique):
    """Character's equipped weapon."""

    id: int
    icon: str
    name: str
    rarity: int
    description: str = Aliased("desc")
    level: int
    type: str = Aliased("type_name")
    ascension: int = Aliased("promote_level")
    refinement: int = Aliased("affix_level")


class ArtifactSetEffect(APIModel):
    """Effect of an artifact set."""

    pieces: int = Aliased("activation_number")
    effect: str
    enabled: bool = False

    class Config:
        # this is for the "enabled" field, hopefully nobody abuses this
        allow_mutation = True


class ArtifactSet(APIModel, Unique):
    """Artifact set."""

    id: int
    name: str
    effects: typing.Sequence[ArtifactSetEffect] = Aliased("affixes")


class Artifact(APIModel, Unique):
    """Character's equipped artifact."""

    id: int
    icon: str
    name: str
    pos_name: str
    pos: int
    rarity: int
    level: int
    set: ArtifactSet


class Constellation(APIModel, Unique):
    """Character constellation."""

    id: int
    icon: str
    pos: int
    name: str
    effect: str
    activated: bool = Aliased("is_actived")

    @property
    def scaling(self) -> bool:
        """Whether the constellation is simply for talent scaling"""
        return "U" in self.icon


class Outfit(APIModel, Unique):
    """Outfit of a character."""

    id: int
    icon: str
    name: str


class Character(PartialCharacter):
    """Character with equipment."""

    weapon: CharacterWeapon
    artifacts: typing.Sequence[Artifact] = Aliased("reliquaries")
    constellations: typing.Sequence[Constellation]
    outfits: typing.Sequence[Outfit] = Aliased("costumes")

    @pydantic.validator("artifacts")
    def __add_artifact_effect_enabled(cls, artifacts: typing.Sequence[Artifact]) -> typing.Sequence[Artifact]:
        sets: typing.Dict[int, typing.List[Artifact]] = {}
        for arti in artifacts:
            sets.setdefault(arti.set.id, []).append(arti)

        for artifact in artifacts:
            for effect in artifact.set.effects:
                if effect.pieces <= len(sets[artifact.set.id]):
                    effect.enabled = True

        return artifacts
