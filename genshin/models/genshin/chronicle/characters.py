"""Genshin chronicle character."""

import enum
import typing
from collections import defaultdict

import pydantic

from genshin.models.genshin import character
from genshin.models.model import APIModel

__all__ = [
    "Artifact",
    "ArtifactProperty",
    "ArtifactSet",
    "ArtifactSetEffect",
    "Character",
    "CharacterSkill",
    "CharacterWeapon",
    "Constellation",
    "DetailArtifact",
    "DetailCharacterWeapon",
    "GenshinDetailCharacter",
    "GenshinDetailCharacters",
    "GenshinWeaponType",
    "Outfit",
    "PartialCharacter",
    "PropInfo",
    "PropertyValue",
    "SkillAffix",
]


class GenshinWeaponType(enum.IntEnum):
    """Character weapon types."""

    SWORD = 1
    CATALYST = 10
    CLAYMORE = 11
    BOW = 12
    POLEARM = 13


class PartialCharacter(character.BaseCharacter):
    """Character without any equipment."""

    level: int
    friendship: int = pydantic.Field(alias="fetter")
    constellation: int = pydantic.Field(alias="actived_constellation_num")


class CharacterWeapon(APIModel):
    """Character's equipped weapon."""

    id: int
    icon: str
    name: str
    rarity: int
    description: str = pydantic.Field(alias="desc")
    level: int
    type: str = pydantic.Field(alias="type_name")
    ascension: int = pydantic.Field(alias="promote_level")
    refinement: int = pydantic.Field(alias="affix_level")


class ArtifactSetEffect(APIModel):
    """Effect of an artifact set."""

    required_piece_num: int = pydantic.Field(alias="activation_number")
    effect: str
    active: bool = pydantic.Field(alias="enabled", default=False)


class ArtifactSet(APIModel):
    """Artifact set."""

    id: int
    name: str
    effects: typing.Sequence[ArtifactSetEffect] = pydantic.Field(alias="affixes")


class Artifact(APIModel):
    """Character's equipped artifact."""

    id: int
    icon: str
    name: str
    pos_name: str
    pos: int
    rarity: int
    level: int
    set: ArtifactSet


class Constellation(APIModel):
    """Character constellation."""

    id: int
    icon: str
    pos: int
    name: str
    effect: str
    activated: bool = pydantic.Field(alias="is_actived")

    @property
    def scaling(self) -> bool:
        """Whether the constellation is simply for talent scaling"""
        return "U" in self.icon


class Outfit(APIModel):
    """Outfit of a character."""

    id: int
    icon: str
    name: str


class Character(PartialCharacter):
    """Character with equipment."""

    weapon: CharacterWeapon
    artifacts: typing.Sequence[Artifact] = pydantic.Field(alias="reliquaries")
    constellations: typing.Sequence[Constellation]
    outfits: typing.Sequence[Outfit] = pydantic.Field(alias="costumes")

    @pydantic.field_validator("artifacts")
    @classmethod
    def __enable_artifact_set_effects(cls, artifacts: typing.Sequence[Artifact]) -> typing.Sequence[Artifact]:
        set_nums: typing.DefaultDict[int, int] = defaultdict(int)
        for arti in artifacts:
            set_nums[arti.set.id] += 1

        for artifact in artifacts:
            for effect in artifact.set.effects:
                if effect.required_piece_num <= set_nums[artifact.set.id]:
                    # To bypass model's immutability
                    effect = effect.model_copy(update={"active": True})

        return artifacts


class PropInfo(APIModel):
    """A property such as Crit Rate, HP, HP%."""

    type: int = pydantic.Field(alias="property_type")
    name: str
    icon: typing.Optional[str]
    filter_name: str

    @pydantic.field_validator("name", "filter_name")
    @classmethod
    def __fix_names(cls, value: str) -> str:
        r"""Fix "\xa0" in Crit Damage + Crit Rate names."""
        return value.replace("\xa0", " ")


class PropertyValue(APIModel):
    """A property with a value."""

    base: str
    add: str
    final: str
    info: PropInfo


class DetailCharacterWeapon(CharacterWeapon):
    """Detailed Genshin Weapon with main/sub stats."""

    main_stat: PropertyValue = pydantic.Field(alias="main_property")
    sub_stat: typing.Optional[PropertyValue] = pydantic.Field(alias="sub_property")


class ArtifactProperty(APIModel):
    """Artifact's Property value & roll count."""

    value: str
    times: int
    info: PropInfo


class DetailArtifact(Artifact):
    """Detailed artifact with main/sub stats."""

    main_stat: ArtifactProperty = pydantic.Field(alias="main_property")
    sub_stats: typing.Sequence[ArtifactProperty] = pydantic.Field(alias="sub_property_list")


class SkillAffix(APIModel):
    """Skill affix texts."""

    name: str
    value: str


class CharacterSkill(APIModel):
    """Character's skill."""

    id: int = pydantic.Field(alias="skill_id")
    skill_type: int
    name: str
    level: int

    description: str = pydantic.Field(alias="desc")
    affixes: typing.Sequence[SkillAffix] = pydantic.Field(alias="skill_affix_list")
    icon: str
    is_unlocked: bool = pydantic.Field(alias="is_unlock")


class GenshinDetailCharacter(PartialCharacter):
    """Full Detailed Genshin Character"""

    is_chosen: bool

    # display_image is a different image that is returned by the full character endpoint, but it is not the full gacha art.
    display_image: str = pydantic.Field(alias="image")

    weapon_type: GenshinWeaponType
    weapon: DetailCharacterWeapon

    costumes: typing.Sequence[Outfit]

    artifacts: typing.Sequence[DetailArtifact] = pydantic.Field(alias="relics")
    constellations: typing.Sequence[Constellation]

    skills: typing.Sequence[CharacterSkill]

    selected_properties: typing.Sequence[PropertyValue]
    base_properties: typing.Sequence[PropertyValue]
    extra_properties: typing.Sequence[PropertyValue]
    element_properties: typing.Sequence[PropertyValue]


class GenshinDetailCharacters(APIModel):
    """Genshin character list."""

    characters: typing.Sequence[GenshinDetailCharacter] = pydantic.Field(alias="list")

    property_map: typing.Mapping[str, PropInfo]
    possible_artifact_stats: typing.Mapping[str, typing.Sequence[PropInfo]] = pydantic.Field(
        alias="relic_property_options"
    )

    artifact_wiki: typing.Mapping[str, str] = pydantic.Field(alias="relic_wiki")
    weapon_wiki: typing.Mapping[str, str]
    avatar_wiki: typing.Mapping[str, str]

    @pydantic.model_validator(mode="before")
    @classmethod
    def __fill_prop_info(cls, values: typing.Dict[str, typing.Any]) -> typing.Mapping[str, typing.Any]:
        """Fill property info from properety_map."""
        relic_property_options: typing.Dict[str, list[int]] = values.get("possible_artifact_stats", {})
        prop_map: typing.Dict[str, typing.Dict[str, typing.Any]] = values.get("property_map", {})
        characters: list[typing.Dict[str, typing.Any]] = values.get("characters", [])

        # Map properties to artifacts
        new_relic_prop_options: typing.Dict[str, list[typing.Dict[str, typing.Any]]] = {}
        for relic_type, properties in relic_property_options.items():
            formatted_properties: list[typing.Dict[str, typing.Any]] = [
                prop_map[str(prop)] for prop in properties if str(prop) in prop_map
            ]
            new_relic_prop_options[relic_type] = formatted_properties

        # Override possible_artifact_stats
        values["possible_artifact_stats"] = new_relic_prop_options

        for char in characters:
            # Extract character info from .base
            for key, value in char["base"].items():
                if key == "weapon":  # Ignore .weapon in base as it does not have full info.
                    continue
                char[key] = value

            # Map properties to main/sub stat for weapon.
            main_property = char["weapon"]["main_property"]
            char["weapon"]["main_property"]["info"] = prop_map[str(main_property["property_type"])]
            if sub_property := char["weapon"]["sub_property"]:
                char["weapon"]["sub_property"]["info"] = prop_map[str(sub_property["property_type"])]

            # Map properties to artifacts
            for artifact in char["relics"]:
                main_property = artifact["main_property"]
                artifact["main_property"]["info"] = prop_map[str(main_property["property_type"])]
                for sub_property in artifact["sub_property_list"]:
                    sub_property["info"] = prop_map[str(sub_property["property_type"])]

            # Map character properties
            for prop in (
                char["base_properties"]
                + char["selected_properties"]
                + char["extra_properties"]
                + char["element_properties"]
            ):
                prop["info"] = prop_map[str(prop["property_type"])]

        return values
