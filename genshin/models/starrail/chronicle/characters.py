"""Starrail chronicle character."""

import enum
from collections.abc import Mapping, Sequence
from typing import Any, Optional

import pydantic

from genshin.models.model import Aliased, APIModel

from .. import character

__all__ = [
    "CharacterProperty",
    "ModifyRelicProperty",
    "PropertyInfo",
    "Rank",
    "RecommendProperty",
    "Relic",
    "RelicProperty",
    "Skill",
    "SkillStage",
    "StarRailDetailCharacter",
    "StarRailDetailCharacters",
    "StarRailEquipment",
    "StarRailPath",
]


class StarRailPath(enum.IntEnum):
    """StarRail character path."""

    DESTRUCTION = 1
    THE_HUNT = 2
    ERUDITION = 3
    HARMONY = 4
    NIHILITY = 5
    PRESERVATION = 6
    ABUNDANCE = 7
    REMEMBRANCE = 8


class StarRailEquipment(APIModel):
    """Character equipment."""

    id: int
    level: int
    rank: int
    name: str
    desc: str
    icon: str
    rarity: int
    wiki: str


class PropertyInfo(APIModel):
    """Relic property info."""

    property_type: int
    name: str
    icon: str
    property_name_relic: str
    property_name_filter: str


class RelicProperty(APIModel):
    """Relic property."""

    property_type: int
    value: str
    times: int
    preferred: bool
    recommended: bool
    info: PropertyInfo


class Relic(APIModel):
    """Character relic."""

    id: int
    level: int
    pos: int
    name: str
    desc: str
    icon: str
    rarity: int
    wiki: str
    main_property: RelicProperty
    properties: Sequence[RelicProperty]


class Rank(APIModel):
    """Character rank."""

    id: int
    pos: int
    name: str
    icon: str
    desc: str
    is_unlocked: bool


class CharacterProperty(APIModel):
    """Base character property."""

    property_type: int
    base: str
    add: str
    final: str
    preferred: bool
    recommended: bool
    info: PropertyInfo


class SkillStage(APIModel):
    """Character skill stage."""

    name: str
    desc: str
    level: int
    remake: str
    item_url: str
    is_activated: bool
    is_rank_work: bool


class Skill(APIModel):
    """Character skill."""

    point_id: str
    point_type: int
    item_url: str
    level: int
    is_activated: bool
    is_rank_work: bool
    pre_point: str
    anchor: str
    remake: str
    skill_stages: Sequence[SkillStage]


class RecommendProperty(APIModel):
    """Character recommended and preferred properties."""

    recommend_relic_properties: Sequence[int]
    custom_relic_properties: Sequence[int]
    is_custom_property_valid: bool


class StarRailDetailCharacter(character.StarRailPartialCharacter):
    """StarRail character with equipment and relics."""

    image: str
    equip: Optional[StarRailEquipment]
    relics: Sequence[Relic]
    ornaments: Sequence[Relic]
    ranks: Sequence[Rank]
    properties: Sequence[CharacterProperty]
    path: StarRailPath = Aliased("base_type")
    figure_path: str
    skills: Sequence[Skill]

    @pydantic.computed_field
    @property
    def is_wearing_outfit(self) -> bool:
        """Whether the character is wearing an outfit."""
        return "avatar_skin_image" in self.image


class ModifyRelicProperty(APIModel):
    """Modify relic property."""

    property_type: int
    modify_property_type: int


class StarRailDetailCharacters(APIModel):
    """StarRail characters."""

    avatar_list: Sequence[StarRailDetailCharacter]
    equip_wiki: Mapping[str, str]
    relic_wiki: Mapping[str, str]
    property_info: Mapping[str, PropertyInfo]
    recommend_property: Mapping[str, RecommendProperty]
    relic_properties: Sequence[ModifyRelicProperty]

    @pydantic.model_validator(mode="before")
    def __fill_additional_fields(cls, values: Mapping[str, Any]) -> Mapping[str, Any]:
        """Fill additional fields for convenience."""
        characters = values.get("avatar_list", [])
        props_info = values.get("property_info", {})
        rec_props = values.get("recommend_property", {})
        equip_wiki = values.get("equip_wiki", {})
        relic_wiki = values.get("relic_wiki", {})

        for char in characters:
            char_id = str(char["id"])
            char_rec_props = rec_props[char_id]["recommend_relic_properties"]
            char_custom_props = rec_props[char_id]["custom_relic_properties"]

            for relic in char["relics"] + char["ornaments"]:
                prop_type = relic["main_property"]["property_type"]
                relic["main_property"]["info"] = props_info[str(prop_type)]
                relic["main_property"]["recommended"] = prop_type in char_rec_props
                relic["main_property"]["preferred"] = prop_type in char_custom_props

                for prop in relic["properties"]:
                    prop_type = prop["property_type"]
                    prop["recommended"] = prop_type in char_rec_props
                    prop["preferred"] = prop_type in char_custom_props
                    prop["info"] = props_info[str(prop_type)]

                relic["wiki"] = relic_wiki.get(str(relic["id"]), "")

            for prop in char["properties"]:
                prop_type = prop["property_type"]
                prop["recommended"] = prop_type in char_rec_props
                prop["preferred"] = prop_type in char_custom_props
                prop["info"] = props_info[str(prop_type)]

            if char["equip"]:
                char["equip"]["wiki"] = equip_wiki.get(str(char["equip"]["id"]), "")

        return values
