import enum
import typing

from genshin.models.model import Aliased, APIModel, Unique

if typing.TYPE_CHECKING:
    import pydantic.v1 as pydantic
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
        import pydantic

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
    "ZZZSkillType",
    "ZZZSpeciality",
    "ZZZPropertyType",
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

    name: str = Aliased("property_name")
    type: typing.Union[int, ZZZPropertyType] = Aliased("property_id")
    value: str = Aliased("base")

    @pydantic.validator("type", pre=True)
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
    icon: str
    refinement: typing.Literal[1, 2, 3, 4, 5] = Aliased("star")
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
