"""Genshin serenitea pot replica display models."""

from __future__ import annotations

import enum
import typing

import pydantic

from genshin.models.model import APIModel

__all__ = [
    "TCGBaseCard",
    "TCGCard",
    "TCGCardType",
    "TCGCharacterCard",
    "TCGCharacterTalent",
    "TCGCost",
    "TCGPartialCard",
    "TCGPreview",
]


class TCGCardType(str, enum.Enum):
    """TCG card type."""

    CHARACTER = "CardTypeCharacter"
    EQUIPMENT = "CardTypeModify"
    ASSIST = "CardTypeAssist"
    EVENT = "CardTypeEvent"


class TCGPartialCard(APIModel):
    """Partial TCG card data."""

    id: int
    image: str


class TCGPreview(APIModel):
    """Preview of TCG stats."""

    character_cards: int = pydantic.Field(alias="avatar_card_num_gained")
    action_cards: int = pydantic.Field(alias="action_card_num_gained")

    total_character_cards: int = pydantic.Field(alias="avatar_card_num_total")
    total_action_cards: int = pydantic.Field(alias="action_card_num_total")

    level: int
    nickname: str

    cards: typing.Sequence[TCGPartialCard] = pydantic.Field(alias="covers")


class TCGCharacterTalent(APIModel):
    """TCG character talent."""

    id: int
    name: str
    description: str = pydantic.Field(alias="desc")
    type: str = pydantic.Field(alias="tag")


class TCGCost(APIModel):
    """TCG cost."""

    element: str = pydantic.Field(alias="cost_type")
    value: int = pydantic.Field(alias="cost_value")

    @pydantic.field_validator("element")
    @classmethod
    def __fix_element(cls, value: str) -> str:
        return {
            "CostTypeCryo": "Cryo",
            "CostTypeDendro": "Dendro",
            "CostTypeElectro": "Electro",
            "CostTypeGeo": "Geo",
            "CostTypeHydro": "Hydro",
            "CostTypePyro": "Pyro",
            "CostTypeAnemo": "Anemo",
            "CostTypeSame": "Same",
            "CostTypeVoid": "Void",
        }.get(value, value)


class TCGBaseCard(TCGPartialCard):
    """TCG card."""

    type: TCGCardType = pydantic.Field(alias="card_type")

    name: str
    proficiency: int
    rank_id: int
    usages: int = pydantic.Field(alias="use_count")

    image_tags: typing.Sequence[str] = pydantic.Field(alias="tags")

    wiki_url: str = pydantic.Field(alias="card_wiki")


class TCGCharacterCard(TCGBaseCard):
    """TCG character card."""

    type: typing.Literal[TCGCardType.CHARACTER] = pydantic.Field(alias="card_type")

    name: str
    health: int = pydantic.Field(alias="hp")

    talents: typing.Sequence[TCGCharacterTalent] = pydantic.Field(alias="card_skills")


class TCGCard(TCGBaseCard):
    """TCG equipment card."""

    type: typing.Literal[TCGCardType.EQUIPMENT, TCGCardType.ASSIST, TCGCardType.EVENT] = pydantic.Field(
        alias="card_type"
    )

    cost: typing.Sequence[TCGCost] = pydantic.Field(alias="action_cost")
    description: str = pydantic.Field(alias="desc")
