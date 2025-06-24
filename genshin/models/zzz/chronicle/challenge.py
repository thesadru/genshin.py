import datetime
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, DateTime, TZDateTime, prevent_enum_error
from genshin.models.zzz.character import ZZZElementType, ZZZSpecialty

__all__ = (
    "ChallengeBangboo",
    "DeadlyAssault",
    "DeadlyAssaultAgent",
    "DeadlyAssaultBoss",
    "DeadlyAssaultBuff",
    "DeadlyAssaultChallenge",
    "ShiyuDefense",
    "ShiyuDefenseBangboo",
    "ShiyuDefenseBuff",
    "ShiyuDefenseCharacter",
    "ShiyuDefenseFloor",
    "ShiyuDefenseMonster",
    "ShiyuDefenseNode",
)


class ShiyuDefenseBangboo(APIModel):
    """Shiyu Defense bangboo model."""

    id: int
    rarity: typing.Literal["S", "A"]
    level: int
    icon: str = Aliased("bangboo_rectangle_url")


class ChallengeBangboo(ShiyuDefenseBangboo):
    """Bangboo model for backward compatibility."""


class ShiyuDefenseCharacter(APIModel):
    """Shiyu Defense character model."""

    id: int
    level: int
    rarity: typing.Literal["S", "A"]
    element: ZZZElementType = Aliased("element_type")
    icon: str = Aliased("role_square_url")
    mindscape: int = Aliased("rank")


class ShiyuDefenseBuff(APIModel):
    """Shiyu Defense buff model."""

    name: str = Aliased("title")
    description: str = Aliased("text")


class ShiyuDefenseMonster(APIModel):
    """Shiyu Defense monster model."""

    id: int
    name: str
    weakness: typing.Union[ZZZElementType, int] = Aliased("weak_element_type")
    level: int

    @pydantic.field_validator("weakness", mode="before")
    def __convert_weakness(cls, v: int) -> typing.Union[ZZZElementType, int]:
        return prevent_enum_error(v, ZZZElementType)


class ShiyuDefenseNode(APIModel):
    """Shiyu Defense node model."""

    characters: list[ShiyuDefenseCharacter] = Aliased("avatars")
    bangboo: typing.Optional[ShiyuDefenseBangboo] = Aliased("buddy", default=None)
    recommended_elements: list[ZZZElementType] = Aliased("element_type_list")
    enemies: list[ShiyuDefenseMonster] = Aliased("monster_info")
    battle_time: typing.Optional[datetime.timedelta] = None

    @pydantic.field_validator("enemies", mode="before")
    @classmethod
    def __convert_enemies(cls, value: dict[typing.Literal["level", "list"], typing.Any]) -> list[ShiyuDefenseMonster]:
        level = value["level"]
        result: list[ShiyuDefenseMonster] = []
        for monster in value["list"]:
            monster["level"] = level
            result.append(ShiyuDefenseMonster(**monster))
        return result


class ShiyuDefenseFloor(APIModel):
    """Shiyu Defense floor model."""

    index: int = Aliased("layer_index")
    rating: typing.Literal["S", "A", "B"]
    id: int = Aliased("layer_id")
    buffs: list[ShiyuDefenseBuff]
    node_1: ShiyuDefenseNode
    node_2: ShiyuDefenseNode
    challenge_time: TZDateTime = Aliased("floor_challenge_time")
    name: str = Aliased("zone_name")

    @pydantic.field_validator("challenge_time", mode="before")
    @classmethod
    def __parse_datetime(cls, value: typing.Mapping[str, typing.Any]) -> typing.Optional[TZDateTime]:
        if value:
            return datetime.datetime(**value)
        return None


class ShiyuDefense(APIModel):
    """ZZZ Shiyu Defense model."""

    schedule_id: int
    begin_time: typing.Optional[TZDateTime] = Aliased("hadal_begin_time")
    end_time: typing.Optional[TZDateTime] = Aliased("hadal_end_time")
    has_data: bool
    ratings: typing.Mapping[typing.Literal["S", "A", "B"], int] = Aliased("rating_list")
    floors: list[ShiyuDefenseFloor] = Aliased("all_floor_detail")
    fastest_clear_time: int = Aliased("fast_layer_time")
    """Fastest clear time this season in seconds."""
    max_floor: int = Aliased("max_layer")

    @pydantic.field_validator("begin_time", "end_time", mode="before")
    @classmethod
    def __parse_datetime(cls, value: typing.Mapping[str, typing.Any]) -> typing.Optional[TZDateTime]:
        if value:
            return datetime.datetime(**value)
        return None

    @pydantic.field_validator("ratings", mode="before")
    @classmethod
    def __convert_ratings(
        cls, v: list[dict[typing.Literal["times", "rating"], typing.Any]]
    ) -> typing.Mapping[typing.Literal["S", "A", "B"], int]:
        return {d["rating"]: d["times"] for d in v}


class DeadlyAssaultBoss(APIModel):
    """ZZZ Deadly Assault boss."""

    icon: str
    name: str
    background: str = Aliased("bg_icon")
    badge_icon: str = Aliased("race_icon")


class DeadlyAssaultBuff(APIModel):
    """ZZZ Deadly Assault buff model."""

    name: str
    description: str = Aliased("desc")
    icon: str


class DeadlyAssaultAgent(APIModel):
    """ZZZ Deadly Assault agent model."""

    id: int
    level: int
    element: ZZZElementType = Aliased("element_type")
    specialty: ZZZSpecialty = Aliased("avatar_profession")
    rarity: typing.Literal["S", "A"]
    mindscape: int = Aliased("rank")
    icon: str = Aliased("role_square_url")


class DeadlyAssaultChallenge(APIModel):
    """ZZZ Deadly Assault challenge model."""

    score: int
    star: int
    total_star: int
    challenge_time: datetime.datetime

    boss: DeadlyAssaultBoss
    buffs: typing.Sequence[DeadlyAssaultBuff] = Aliased("buffer")
    agents: typing.Sequence[DeadlyAssaultAgent] = Aliased("avatar_list")
    bangboo: typing.Optional[ShiyuDefenseBangboo] = Aliased("buddy", default=None)

    @pydantic.field_validator("challenge_time", mode="before")
    def __parse_datetime(cls, value: typing.Mapping[str, typing.Any]) -> typing.Optional[TZDateTime]:
        if value:
            return datetime.datetime(**value)
        return None

    @pydantic.field_validator("boss", mode="before")
    def __parse_boss(cls, value: typing.List[typing.Mapping[str, typing.Any]]) -> DeadlyAssaultBoss:
        if not value:
            raise ValueError("No boss data provided.")
        return DeadlyAssaultBoss(**value[0])


class DeadlyAssault(APIModel):
    """ZZZ Deadly Assault model."""

    id: int = Aliased("zone_id")
    start_time: typing.Optional[DateTime]
    end_time: typing.Optional[DateTime]

    challenges: typing.Sequence[DeadlyAssaultChallenge] = Aliased("list")
    has_data: bool
    total_score: int
    total_star: int
    rank_percent: str

    nickname: str = Aliased("nick_name")
    player_avatar: str = Aliased("avatar_icon")

    @pydantic.field_validator("rank_percent", mode="before")
    def __parse_rank_percent(cls, value: int) -> str:
        return f"{value / 100}%"
