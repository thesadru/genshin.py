"""Starrail base character model."""

import enum
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, Unique

__all__ = (
    "BaseMemoSprite",
    "BaseRelic",
    "BaseSkill",
    "DetailMemoSprite",
    "DetailRelic",
    "DetailRelicProperty",
    "DetailSkill",
    "FloorCharacter",
    "LineupMemoSprite",
    "LineupRelic",
    "PropertyInfo",
    "Rank",
    "RelicProperty",
    "RogueCharacter",
    "SkillStage",
    "StarRailBaseCharacter",
    "StarRailBaseEquipment",
    "StarRailBaseProperty",
    "StarRailCharacterProperty",
    "StarRailDetailCharacter",
    "StarRailEquipment",
    "StarRailLineupCharacter",
    "StarRailLineupProperty",
    "StarRailPartialCharacter",
    "StarRailPath",
)


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


class StarRailBaseCharacter(APIModel, Unique):
    """Base character model."""

    id: int
    element: str
    rarity: int
    icon: str


class StarRailPartialCharacter(StarRailBaseCharacter):
    """Character without any equipment."""

    name: str
    level: int
    rank: int


class FloorCharacter(StarRailBaseCharacter):
    """Character in a floor."""

    level: int
    rank: int


class RogueCharacter(StarRailBaseCharacter):
    """Rogue character model."""

    level: int
    rank: int


class StarRailBaseEquipment(APIModel):
    """HSR character light cone."""

    id: int
    level: int
    rank: int
    name: str
    desc: str
    icon: str
    rarity: int


class StarRailEquipment(StarRailBaseEquipment):
    """HSR character light cone."""

    wiki: str


class PropertyInfo(APIModel):
    """Relic property info."""

    property_type: int
    name: str
    icon: str
    property_name_relic: str
    property_name_filter: str


class RelicProperty(APIModel):
    """HSR relic property."""

    property_type: int
    value: str
    times: int
    name: str = Aliased("property_name")
    icon: str


class DetailRelicProperty(APIModel):
    """Relic property for detailed character."""

    property_type: int
    value: str
    times: int
    preferred: bool
    recommended: bool
    info: PropertyInfo


class BaseRelic(APIModel):
    """HSR base relic."""

    id: int
    pos: int
    rarity: int


class LineupRelic(BaseRelic):
    """HSR lineup relic."""

    set_name: str
    set_num: int

    main_property: RelicProperty
    properties: typing.Sequence[RelicProperty]

    wiki: str = Aliased("wiki_url")


class DetailRelic(BaseRelic):
    """HSR character relic."""

    level: int
    name: str
    desc: str
    icon: str

    wiki: str
    main_property: DetailRelicProperty
    properties: typing.Sequence[DetailRelicProperty]


class Rank(APIModel):
    """HSR character eidolon."""

    id: int
    pos: int
    name: str
    icon: str
    desc: str
    is_unlocked: bool


class StarRailLineupProperty(APIModel):
    """HSR character/memosprite property for lineup simulator."""

    property_type: int
    base: str
    add: str
    final: str
    name: str = Aliased("property_name")
    icon: str

    base_float: float
    add_float: float
    final_float: float


class StarRailBaseProperty(APIModel):
    """HSR detail character endpoint base property (for memosprite.)"""

    property_type: int
    info: PropertyInfo
    base: str
    add: str
    final: str


class StarRailCharacterProperty(StarRailBaseProperty):
    """HSR property for detailed character, with preferred and recommended flags."""

    preferred: bool
    recommended: bool


class SkillStage(APIModel):
    """Character skill stage."""

    name: str
    desc: str
    level: int
    remake: str
    item_url: str
    is_activated: bool
    is_rank_work: bool


class BaseSkill(APIModel):
    """HSR character/memosprite skill."""

    point_id: str
    point_type: int
    item_url: str
    level: int
    is_activated: bool
    is_rank_work: bool
    pre_point: str
    anchor: str
    remake: str


class DetailSkill(BaseSkill):
    """HSR character/memosprite skill for detail character."""

    skill_stages: typing.Sequence[SkillStage]


class BaseMemoSprite(APIModel):
    """HSR base memosprite."""

    id: int = Aliased("servant_id")
    name: str = Aliased("servant_name")
    icon: str = Aliased("servant_icon")


class LineupMemoSprite(BaseMemoSprite):
    """HSR lineup memosprite."""

    properties: typing.Sequence[StarRailLineupProperty] = Aliased("servant_properties")
    skills: typing.Sequence[BaseSkill] = Aliased("servant_skills")


class DetailMemoSprite(BaseMemoSprite):
    """HSR memosprite for detail character."""

    properties: typing.Sequence[StarRailBaseProperty] = Aliased("servant_properties")
    skills: typing.Sequence[DetailSkill] = Aliased("servant_skills")


class StarRailDetailCharacter(StarRailPartialCharacter):
    """StarRail character with equipment and relics."""

    image: str
    equip: typing.Optional[StarRailEquipment]
    relics: typing.Sequence[DetailRelic]
    ornaments: typing.Sequence[DetailRelic]
    ranks: typing.Sequence[Rank]
    properties: typing.Sequence[StarRailCharacterProperty]
    path: StarRailPath = Aliased("base_type")
    figure_path: str
    skills: typing.Sequence[DetailSkill]
    memosprite: typing.Optional[DetailMemoSprite] = Aliased("servant_detail")

    @property
    def is_wearing_outfit(self) -> bool:
        """Whether the character is wearing an outfit."""
        return "avatar_skin_image" in self.image

    @pydantic.field_validator("memosprite", mode="before")
    @classmethod
    def __return_none(
        cls, value: typing.Optional[typing.Dict[str, typing.Any]]
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """Return None if memosprite ID is 0."""
        if value is None:
            return None
        if value.get("servant_id", "0") == "0":
            return None
        return value


class StarRailLineupCharacter(StarRailPartialCharacter):
    """HSR lineup simulator character."""

    equip: typing.Optional[StarRailBaseEquipment]
    relics: typing.Sequence[LineupRelic]
    ranks: typing.Sequence[Rank]
    properties: typing.Sequence[StarRailLineupProperty]
    skills: typing.Sequence[BaseSkill]
    memosprite: typing.Optional[LineupMemoSprite] = Aliased("servant_detail")

    path: StarRailPath = Aliased("base_type")
    figure_path: str
