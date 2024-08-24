import enum
import typing

import pydantic

from genshin.models.model import APIModel

__all__ = (
    "AgentSkill",
    "AgentSkillItem",
    "DiscSetEffect",
    "WEngine",
    "ZZZAgentProperty",
    "ZZZAgentRank",
    "ZZZBaseAgent",
    "ZZZDisc",
    "ZZZElementType",
    "ZZZFullAgent",
    "ZZZPartialAgent",
    "ZZZProperty",
    "ZZZPropertyType",
    "ZZZSkillType",
    "ZZZSpecialty",
)


class ZZZElementType(enum.IntEnum):
    """ZZZ element type."""

    PHYSICAL = 200
    FIRE = 201
    ICE = 202
    ELECTRIC = 203
    ETHER = 205


class ZZZSpecialty(enum.IntEnum):
    """ZZZ agent compatible specialty."""

    ATTACK = 1
    STUN = 2
    ANOMALY = 3
    SUPPORT = 4
    DEFENSE = 5


class ZZZBaseAgent(APIModel):
    """ZZZ base agent model."""

    id: int  # 4 digit number
    element: ZZZElementType = pydantic.Field(alias="element_type")
    rarity: typing.Literal["S", "A"]
    name: str = pydantic.Field(alias="name_mi18n")
    full_name: str = pydantic.Field(alias="full_name_mi18n")
    specialty: ZZZSpecialty = pydantic.Field(alias="avatar_profession")
    faction_icon: str = pydantic.Field(alias="group_icon_path")
    flat_icon: str = pydantic.Field(alias="hollow_icon_path")

    @property
    def square_icon(self) -> str:
        """Example: https://act-webstatic.hoyoverse.com/game_record/zzz/role_square_avatar/role_square_avatar_1131.png"""
        return (
            f"https://act-webstatic.hoyoverse.com/game_record/zzz/role_square_avatar/role_square_avatar_{self.id}.png"
        )

    @property
    def rectangle_icon(self) -> str:
        """Example: https://act-webstatic.hoyoverse.com/game_record/zzz/role_rectangle_avatar/role_rectangle_avatar_1131.png"""
        return f"https://act-webstatic.hoyoverse.com/game_record/zzz/role_rectangle_avatar/role_rectangle_avatar_{self.id}.png"

    @property
    def banner_icon(self) -> str:
        """Example: https://act-webstatic.hoyoverse.com/game_record/zzz/role_vertical_painting/role_vertical_painting_1131.png"""
        return f"https://act-webstatic.hoyoverse.com/game_record/zzz/role_vertical_painting/role_vertical_painting_{self.id}.png"


class ZZZPartialAgent(ZZZBaseAgent):
    """Character without any equipment."""

    level: int
    rank: int
    """Also known as Mindscape Cinema in-game."""


class ZZZPropertyType(enum.IntEnum):
    """ZZZ property type."""

    # Agent prop
    AGENT_HP = 1
    AGENT_ATK = 2
    AGENT_DEF = 3
    AGENT_IMPACT = 4
    AGENT_CRIT_RATE = 5
    AGENT_CRIT_DMG = 6
    AGENT_ANOMALY_MASTERY = 7
    AGENT_ANOMALY_PROFICIENCY = 8
    AGENT_PEN_RATIO = 9
    AGENT_ENERGY_GEN = 10

    # Disc drive
    DISC_HP = 11103
    DISC_ATK = 12103
    DISC_DEF = 13103
    DISC_PEN = 23203
    DISC_BONUS_PHYSICAL_DMG = 31503
    DISC_BONUS_FIRE_DMG = 31603
    DISC_BONUS_ICE_DMG = 31703
    DISC_BONUS_ELECTRIC_DMG = 31803
    DISC_BONUS_ETHER_DMG = 31903

    # W-engine
    ENGINE_HP = 11102
    ENGINE_BASE_ATK = 12101
    ENGINE_ATK = 12102
    ENGINE_DEF = 13102
    ENGINE_ENERGY_REGEN = 30502

    # Disc drive and w-engine shared
    CRIT_RATE = 20103
    CRIT_DMG = 21103
    ANOMALY_PROFICIENCY = 31203
    PEN_RATIO = 23103
    IMPACT = 12202


class ZZZProperty(APIModel):
    """A property (stat) for disc or w-engine."""

    name: str = pydantic.Field(alias="property_name")
    type: typing.Union[int, ZZZPropertyType] = pydantic.Field(alias="property_id")
    value: str = pydantic.Field(alias="base")

    @pydantic.field_validator("type", mode="before")
    @classmethod
    def __cast_id(cls, v: int) -> typing.Union[int, ZZZPropertyType]:
        # Prevent enum crash
        try:
            return ZZZPropertyType(v)
        except ValueError:
            return v


class ZZZAgentProperty(ZZZProperty):
    """A property model, but for agents."""

    add: str
    final: str


class DiscSetEffect(APIModel):
    """A disc set effect."""

    id: int = pydantic.Field(alias="suit_id")
    name: str
    owned_num: int = pydantic.Field(alias="own")
    two_piece_description: str = pydantic.Field(alias="desc1")
    four_piece_description: str = pydantic.Field(alias="desc2")


class WEngine(APIModel):
    """A ZZZ W-engine, it's like a weapon."""

    id: int
    level: int
    name: str
    icon: str
    refinement: typing.Literal[1, 2, 3, 4, 5] = pydantic.Field(alias="star")
    rarity: typing.Literal["B", "A", "S"]
    properties: typing.Sequence[ZZZProperty]
    main_properties: typing.Sequence[ZZZProperty]
    effect_title: str = pydantic.Field(alias="talent_title")
    effect_description: str = pydantic.Field(alias="talent_content")
    profession: ZZZSpecialty


class ZZZDisc(APIModel):
    """A ZZZ disc, like an artifact in Genshin."""

    id: int
    level: int
    name: str
    icon: str
    rarity: typing.Literal["B", "A", "S"]
    main_properties: typing.Sequence[ZZZProperty]
    properties: typing.Sequence[ZZZProperty]
    set_effect: DiscSetEffect = pydantic.Field(alias="equip_suit")
    position: int = pydantic.Field(alias="equipment_type")


class ZZZSkillType(enum.IntEnum):
    """ZZZ agent skill type."""

    BASIC_ATTACK = 0
    DODGE = 2
    ASSIST = 6
    SPECIAL_ATTACK = 1
    CHAIN_ATTACK = 3
    CORE_SKILL = 5


class AgentSkillItem(APIModel):
    """An agent skill item."""

    title: str
    text: str


class AgentSkill(APIModel):
    """ZZZ agent skill model."""

    level: int
    type: ZZZSkillType = pydantic.Field(alias="skill_type")
    items: typing.Sequence[AgentSkillItem]
    """One skill can have different forms (?), so there are multiple 'items'."""


class ZZZAgentRank(APIModel):
    """ZZZ agent rank model."""

    id: int
    name: str
    description: str = pydantic.Field(alias="desc")
    position: int = pydantic.Field(alias="pos")
    unlocked: bool = pydantic.Field(alias="is_unlocked")


class ZZZFullAgent(ZZZBaseAgent):
    """Character with equipment."""

    level: int
    rank: int
    """Also known as Mindscape Cinema in-game."""
    faction_name: str = pydantic.Field(alias="camp_name_mi18n")
    properties: typing.Sequence[ZZZAgentProperty]
    discs: typing.Sequence[ZZZDisc] = pydantic.Field(alias="equip")
    w_engine: typing.Optional[WEngine] = pydantic.Field(alias="weapon", default=None)
    skills: typing.Sequence[AgentSkill]
    ranks: typing.Sequence[ZZZAgentRank]
    """Also known as Mindscape Cinemas in-game."""
