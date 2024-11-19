"""Genshin chronicle character."""

import enum
import typing

import pydantic

from genshin.models.genshin import character
from genshin.models.model import Aliased, APIModel, Unique

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
    friendship: int = Aliased("fetter")
    constellation: int = Aliased("actived_constellation_num")


class CharacterWeapon(APIModel, Unique):
    """Character's equipped weapon."""

    id: int
    icon: str
    name: str
    rarity: int
    level: int
    type: int
    refinement: int = Aliased("affix_level")


class ArtifactSetEffect(APIModel):
    """Effect of an artifact set."""

    required_piece_num: int = Aliased("activation_number")
    effect: str
    active: bool = Aliased("enabled", default=False)


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
    weapon_type: int


class PropInfo(APIModel):
    """A property such as Crit Rate, HP, HP%."""

    type: int = Aliased("property_type")
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

    main_stat: PropertyValue = Aliased("main_property")
    sub_stat: typing.Optional[PropertyValue] = Aliased("sub_property")
    ascension: int = Aliased("promote_level")


class ArtifactProperty(APIModel):
    """Artifact's Property value & roll count."""

    value: str
    times: int
    info: PropInfo


class DetailArtifact(Artifact):
    """Detailed artifact with main/sub stats."""

    main_stat: ArtifactProperty = Aliased("main_property")
    sub_stats: typing.Sequence[ArtifactProperty] = Aliased("sub_property_list")


class SkillAffix(APIModel):
    """Skill affix texts."""

    name: str
    value: str


class CharacterSkill(APIModel):
    """Character's skill."""

    id: int = Aliased("skill_id")
    skill_type: int
    name: str
    level: int

    description: str = Aliased("desc")
    affixes: typing.Sequence[SkillAffix] = Aliased("skill_affix_list")
    icon: str
    is_unlocked: bool = Aliased("is_unlock")


class GenshinDetailCharacter(PartialCharacter):
    """Full Detailed Genshin Character"""

    is_chosen: bool

    # display_image is a different image that is returned by the full character endpoint, but it is not the full gacha art.
    display_image: str = Aliased("image")

    weapon_type: GenshinWeaponType
    weapon: DetailCharacterWeapon

    costumes: typing.Sequence[Outfit]

    artifacts: typing.Sequence[DetailArtifact] = Aliased("relics")
    constellations: typing.Sequence[Constellation]

    skills: typing.Sequence[CharacterSkill]

    selected_properties: typing.Sequence[PropertyValue]
    base_properties: typing.Sequence[PropertyValue]
    extra_properties: typing.Sequence[PropertyValue]
    element_properties: typing.Sequence[PropertyValue]


class GenshinDetailCharacters(APIModel):
    """Genshin character list."""

    characters: typing.Sequence[GenshinDetailCharacter] = Aliased("list")

    property_map: typing.Mapping[str, PropInfo]
    possible_artifact_stats: typing.Mapping[str, typing.Sequence[PropInfo]] = Aliased("relic_property_options")

    artifact_wiki: typing.Mapping[str, str] = Aliased("relic_wiki")
    weapon_wiki: typing.Mapping[str, str]
    avatar_wiki: typing.Mapping[str, str]

    @pydantic.model_validator(mode="before")
    def __fill_prop_info(cls, values: dict[str, typing.Any]) -> typing.Mapping[str, typing.Any]:
        """Fill property info from properety_map."""
        relic_property_options: dict[str, list[int]] = values.get("relic_property_options", {})
        prop_map: dict[str, dict[str, typing.Any]] = values.get("property_map", {})
        characters: list[dict[str, typing.Any]] = values.get("list", [])

        # Map properties to artifacts
        new_relic_prop_options: dict[str, list[dict[str, typing.Any]]] = {}
        for relic_type, properties in relic_property_options.items():
            formatted_properties: list[dict[str, typing.Any]] = [
                prop_map[str(prop)] for prop in properties if str(prop) in prop_map
            ]
            new_relic_prop_options[relic_type] = formatted_properties

        # Override relic_property_options
        values["relic_property_options"] = new_relic_prop_options

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
