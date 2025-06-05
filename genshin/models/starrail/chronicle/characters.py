"""Starrail chronicle character."""

import typing
from collections.abc import Mapping, Sequence

import pydantic

from genshin.models.model import APIModel

from .. import character

__all__ = ["StarRailDetailCharacterResponse"]


class RecommendProperty(APIModel):
    """Character recommended and preferred properties."""

    recommend_relic_properties: typing.Sequence[int]
    custom_relic_properties: typing.Sequence[int]
    is_custom_property_valid: bool


class ModifyRelicProperty(APIModel):
    """Modify relic property."""

    property_type: int
    modify_property_type: int


class StarRailDetailCharacterResponse(APIModel):
    """StarRail characters."""

    avatar_list: Sequence[character.StarRailDetailCharacter]
    equip_wiki: Mapping[str, str]
    relic_wiki: Mapping[str, str]
    property_info: Mapping[str, character.PropertyInfo]
    recommend_property: Mapping[str, RecommendProperty]
    relic_properties: Sequence[ModifyRelicProperty]

    @pydantic.model_validator(mode="before")
    def __fill_additional_fields(cls, values: Mapping[str, typing.Any]) -> Mapping[str, typing.Any]:
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

            servant = char.get("servant_detail", {})
            if servant:
                for prop in servant["servant_properties"]:
                    prop_type = prop["property_type"]
                    prop["info"] = props_info[str(prop_type)]

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
