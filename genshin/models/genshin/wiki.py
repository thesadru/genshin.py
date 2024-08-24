"""Genshin wish models."""

import enum
import json
import typing
import unicodedata

import pydantic

from genshin.models.model import APIModel

__all__ = [
    "ArtifactPreview",
    "CharacterPreview",
    "EnemyPreview",
    "WeaponPreview",
    "WikiPage",
    "WikiPageType",
]


class WikiPageType(enum.IntEnum):
    """Wiki page types."""

    UNKNOWN = 0
    CHARACTER = 2
    WEAPON = 4
    ARTIFACT = 5
    ENEMY = 7


class BaseWikiPreview(APIModel):
    """Base wiki preview."""

    id: int = pydantic.Field(alias="entry_page_id")
    icon: str = pydantic.Field(alias="icon_url")
    name: str

    @pydantic.model_validator(mode="before")
    @classmethod
    def __unpack_filter_values(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        filter_values = {
            key.split("_", 1)[1]: value["values"][0]
            for key, value in values.get("filter_values", {}).items()
            if value["values"]
        }
        values.update(filter_values)
        return values

    @pydantic.model_validator(mode="before")
    @classmethod
    def __flatten_display_field(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        values.update(values.get("display_field", {}))
        return values


class CharacterPreview(BaseWikiPreview):
    """Character wiki preview."""

    bonus_attribute: str = pydantic.Field(default="property")
    rarity: int
    region: str = ""
    element: str = pydantic.Field(default="")
    weapon: str

    @pydantic.field_validator("rarity", mode="before")
    @classmethod
    def __extract_rarity(cls, value: typing.Union[int, str]) -> int:
        if not isinstance(value, str):
            return value

        if value[0].isdigit():
            return int(value[0])

        return int(unicodedata.numeric(value[0]))


class WeaponPreview(BaseWikiPreview):
    """Weapon wiki preview."""

    bonus_attribute: str = pydantic.Field(alias="property")
    rarity: int
    type: str

    @pydantic.field_validator("rarity", mode="before")
    @classmethod
    def __extract_rarity(cls, value: typing.Union[int, str]) -> int:
        if not isinstance(value, str):
            return value

        if value[0].isdigit():
            return int(value[0])

        return int(unicodedata.numeric(value[0]))


class ArtifactPreview(BaseWikiPreview):
    """Artifact wiki preview."""

    effect: str

    circlet_icon: str = pydantic.Field(alias="circlet_of_logos_icon_url")
    flower_icon: str = pydantic.Field(alias="flower_of_life_icon_url")
    goblet_icon: str = pydantic.Field(alias="goblet_of_eonothem_icon_url")
    plume_icon: str = pydantic.Field(alias="plume_of_death_icon_url")
    sands_icon: str = pydantic.Field(alias="sands_of_eon_icon_url")

    effects: typing.Mapping[int, str]

    @pydantic.model_validator(mode="before")
    @classmethod
    def __group_effects(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        effects = {
            1: values["single_set_effect"],
            2: values["two_set_effect"],
            4: values["four_set_effect"],
        }
        values["effects"] = {amount: effect for amount, effect in effects.items() if effect}
        return values


class EnemyPreview(BaseWikiPreview):
    """Enemy wiki preview."""

    drop_materials: typing.Sequence[str]

    @pydantic.field_validator("drop_materials", mode="before")
    @classmethod
    def __parse_drop_materials(cls, value: typing.Union[str, typing.Sequence[str]]) -> typing.Sequence[str]:
        return json.loads(value) if isinstance(value, str) else value


_ENTRY_PAGE_MODELS: typing.Mapping[WikiPageType, typing.Type[BaseWikiPreview]] = {
    WikiPageType.CHARACTER: CharacterPreview,
    WikiPageType.WEAPON: WeaponPreview,
    WikiPageType.ARTIFACT: ArtifactPreview,
    WikiPageType.ENEMY: EnemyPreview,
}


class WikiPage(APIModel):
    """Wiki page."""

    id: int
    page_type: WikiPageType = pydantic.Field(alias="menu_id")

    description: str = pydantic.Field(alias="desc")
    header: str = pydantic.Field(alias="header_img_url")
    icon: str = pydantic.Field(alias="icon_url")

    modules: typing.Mapping[str, typing.Mapping[str, typing.Any]]

    @pydantic.field_validator("modules", mode="before")
    @classmethod
    def __format_modules(
        cls,
        value: typing.Union[typing.List[typing.Dict[str, typing.Any]], typing.Dict[str, typing.Any]],
    ) -> typing.Dict[str, typing.Any]:
        if isinstance(value, typing.Mapping):
            return value

        modules: typing.Dict[str, typing.Dict[str, typing.Any]] = {}
        for module in value:
            components: typing.Dict[str, typing.Dict[str, typing.Any]] = {
                component["component_id"]: json.loads(component["data"] or "{}") for component in module["components"]
            }

            components.pop("map", None)  # not worth storing
            if "reliquary_set_effect" in components:
                # Attributes of artifacts should be flattened
                components["baseInfo"]["reliquary_set_effect"] = components.pop("reliquary_set_effect")

            _, modules[module["name"]] = components.popitem()
            continue

        return modules
