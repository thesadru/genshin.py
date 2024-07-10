import enum
import typing

from genshin.models.model import Aliased, APIModel, Unique

__all__ = (
    "ZZZBaseAgent",
    "ZZZElementType",
    "ZZZPartialAgent",
    "ZZZSpeciality",
    "ZZZProperty",
    "ZZZAgentProperty",
    "DiscSetEffect",
    "WEngine",
    "ZZZDisc",
    "ZZZSkillType",
    "AgentSkillItem",
    "AgentSkill",
    "ZZZAgentRank",
    "ZZZFullAgent",
)


class ZZZElementType(enum.IntEnum):
    """ZZZ element type."""

    PHYSICAL = 200
    FIRE = 201
    ICE = 202
    ELECTRIC = 203
    ETHER = 205


class ZZZSpeciality(enum.IntEnum):
    """ZZZ agent compatible speciality."""

    ATTACK = 1
    STUN = 2
    ANOMALY = 3
    SUPPORT = 4
    DEFENSE = 5


class ZZZBaseAgent(APIModel, Unique):
    """ZZZ base agent model."""

    id: int  # 4 digit number
    element: ZZZElementType = Aliased("element_type")
    rarity: typing.Literal["S", "A"]
    name: str = Aliased("name_mi18n")
    speciality: ZZZSpeciality = Aliased("avatar_profession")
    faction_icon: str = Aliased("group_icon_path")
    flat_icon: str = Aliased("hollow_icon_path")

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


class ZZZProperty(APIModel):
    """A property (stat) for disc or w-engine."""

    name: str = Aliased("property_name")
    id: int = Aliased("property_id")
    value: str = Aliased("base")


class ZZZAgentProperty(ZZZProperty):
    """A property model, but for agents."""

    add: str
    final: str


class DiscSetEffect(APIModel):
    """A disc set effect."""

    id: int = Aliased("suit_id")
    name: str
    owned_num: int = Aliased("own")
    two_piece_description: str = Aliased("desc1")
    four_piece_description: str = Aliased("desc2")


class WEngine(APIModel):
    """A ZZZ W-engine, it's like a weapon."""

    id: int
    level: int
    name: str
    star: typing.Literal[1, 2, 3, 4, 5]
    """AKA refinement."""
    rarity: typing.Literal["B", "A", "S"]
    properties: typing.Sequence[ZZZProperty]
    main_properties: typing.Sequence[ZZZProperty]
    effect_title: str = Aliased("talent_title")
    effect_description: str = Aliased("talent_content")
    profession: ZZZSpeciality


class ZZZDisc(APIModel):
    """A ZZZ disc, like an artifact in Genshin."""

    id: int
    level: int
    name: str
    icon: str
    rarity: typing.Literal["B", "A", "S"]
    main_properties: typing.Sequence[ZZZProperty]
    properties: typing.Sequence[ZZZProperty]
    set_effect: DiscSetEffect = Aliased("equip_suit")
    position: int = Aliased("equipment_type")


class ZZZSkillType(enum.IntEnum):
    """ZZZ agent skill type."""

    BASIC_ATTACK = 0
    DODGE = 1
    ASSIST = 2
    SPECIAL_ATTACK = 3
    CHAIN_ATTACK = 4
    CORE_SKILL = 5


class AgentSkillItem(APIModel):
    """An agent skill item."""

    title: str
    text: str


class AgentSkill(APIModel):
    """ZZZ agent skill model."""

    level: int
    skill_type: int
    items: typing.Sequence[AgentSkillItem]
    """One skill can have different forms (?), so there are multiple 'items'."""


class ZZZAgentRank(APIModel):
    """ZZZ agent rank model."""

    id: int
    name: str
    description: str = Aliased("desc")
    position: int = Aliased("pos")
    unlocked: bool = Aliased("is_unlocked")


class ZZZFullAgent(ZZZBaseAgent):
    """Character with equipment."""

    level: int
    rank: int
    """Also known as Mindscape Cinema in-game."""
    faction_name: str = Aliased("camp_name_mi18n")
    properties: typing.Sequence[ZZZAgentProperty]
    discs: typing.Sequence[ZZZDisc] = Aliased("equip")
    w_engine: typing.Optional[WEngine] = Aliased("weapon", default=None)
    skills: typing.Sequence[AgentSkill]
    ranks: typing.Sequence[ZZZAgentRank]
    """Also known as Mindscape Cinemas in-game."""
