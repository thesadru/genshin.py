"""Genshin serenitea pot replica display models."""

from __future__ import annotations

import enum
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, Unique

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


class TCGPartialCard(APIModel, Unique):
    """Partial TCG card data."""

    id: int
    image: str


class TCGPreview(APIModel):
    """Preview of TCG stats."""

    character_cards: int = Aliased("avatar_card_num_gained")
    action_cards: int = Aliased("action_card_num_gained")

    total_character_cards: int = Aliased("avatar_card_num_total")
    total_action_cards: int = Aliased("action_card_num_total")

    level: int
    nickname: str

    cards: typing.Sequence[TCGPartialCard] = Aliased("covers")


class TCGCharacterTalent(APIModel):
    """TCG character talent."""

    id: int
    name: str
    description: str = Aliased("desc")
    type: str = Aliased("tag")


class TCGCost(APIModel):
    """TCG cost."""

    element: str = Aliased("cost_type")
    value: int = Aliased("cost_value")

    @pydantic.field_validator("element")
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

    type: TCGCardType = Aliased("card_type")

    name: str
    proficiency: int
    rank_id: int
    usages: int = Aliased("use_count")

    image_tags: typing.Sequence[str] = Aliased("tags")

    wiki_url: str = Aliased("card_wiki")


class TCGCharacterCard(TCGBaseCard):
    """TCG character card."""

    type: typing.Literal[TCGCardType.CHARACTER] = Aliased("card_type")

    name: str
    health: int = Aliased("hp")

    talents: typing.Sequence[TCGCharacterTalent] = Aliased("card_skills")


class TCGCard(TCGBaseCard):
    """TCG equipment card."""

    type: typing.Literal[TCGCardType.EQUIPMENT, TCGCardType.ASSIST, TCGCardType.EVENT] = Aliased("card_type")

    cost: typing.Sequence[TCGCost] = Aliased("action_cost")
    description: str = Aliased("desc")
