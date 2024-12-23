import datetime
import enum
import typing

import pydantic

from genshin.models.genshin import character
from genshin.models.model import Aliased, APIModel, TZDateTime

__all__ = (
    "Act",
    "ActCharacter",
    "BattleStatCharacter",
    "ImgTheater",
    "ImgTheaterData",
    "TheaterBattleStats",
    "TheaterBuff",
    "TheaterCharaType",
    "TheaterDifficulty",
    "TheaterSchedule",
    "TheaterStats",
)


class TheaterCharaType(enum.IntEnum):
    """The type of character in the context of the imaginarium theater gamemode."""

    NORMAL = 1
    TRIAL = 2
    SUPPORT = 3


class TheaterDifficulty(enum.IntEnum):
    """The difficulty of the imaginarium theater data."""

    UNKNOWN = 0
    EASY = 1
    NORMAL = 2
    HARD = 3
    VISIONARY = 4


class ActCharacter(character.BaseCharacter):
    """A character in an act."""

    type: TheaterCharaType = Aliased("avatar_type")
    level: int


class TheaterBuff(APIModel):
    """Represents either a 'mystery cache' or a 'wondrous boom'."""

    icon: str
    name: str
    description: str = Aliased("desc")
    received_audience_support: bool = Aliased("is_enhanced")
    """Whether external audience support is received."""
    id: int


class Act(APIModel):
    """One act in the theater."""

    characters: typing.Sequence[ActCharacter] = Aliased("avatars")
    mystery_caches: typing.Sequence[TheaterBuff] = Aliased("choice_cards")
    wondroud_booms: typing.Sequence[TheaterBuff] = Aliased("buffs")
    medal_obtained: bool = Aliased("is_get_medal")
    round_id: int
    finish_time: int  # As timestamp
    finish_datetime: TZDateTime = Aliased("finish_date_time")

    @pydantic.field_validator("finish_datetime", mode="before")
    def __parse_datetime(cls, value: typing.Mapping[str, typing.Any]) -> datetime.datetime:
        return datetime.datetime(**value)


class TheaterStats(APIModel):
    """Imaginarium theater stats."""

    difficulty: TheaterDifficulty = Aliased("difficulty_id")
    best_record: int = Aliased("max_round_id")
    """The maximum act the player has reached."""
    heraldry: int  # Not sure what this is
    star_challenge_stellas: typing.Sequence[bool] = Aliased("get_medal_round_list")
    """Whether the player has obtained the medal for each act."""
    fantasia_flowers_used: int = Aliased("coin_num")
    """The number of Fantasia Flowers used."""
    audience_support_trigger_num: int = Aliased("avatar_bonus_num")
    """The number of external audience support triggers."""
    player_assists: int = Aliased("rent_cnt")
    """The number of supporting cast characters assisting other players."""
    medal_num: int
    """The number of medals the player has obtained."""


class TheaterSchedule(APIModel):
    """Imaginarium theater schedule."""

    start_time: int  # As timestamp
    end_time: int  # As timestamp
    schedule_type: int  # Not sure what this is
    id: int = Aliased("schedule_id")
    start_datetime: TZDateTime = Aliased("start_date_time")
    end_datetime: TZDateTime = Aliased("end_date_time")

    @pydantic.field_validator("start_datetime", "end_datetime", mode="before")
    def __parse_datetime(cls, value: typing.Mapping[str, typing.Any]) -> datetime.datetime:
        return datetime.datetime(**value)


class BattleStatCharacter(APIModel):
    """Imaginarium theater battle statistic character."""

    id: int = Aliased("avatar_id")
    icon: str = Aliased("avatar_icon")
    value: int
    rarity: int

    @pydantic.field_validator("value", mode="before")
    def __intify_value(cls, value: str) -> int:
        if not value:
            return 0
        return int(value)


class TheaterBattleStats(APIModel):
    """Imaginarium theater battle statistics."""

    max_defeat_character: typing.Optional[BattleStatCharacter] = Aliased("max_defeat_avatar", default=None)
    max_damage_character: typing.Optional[BattleStatCharacter] = Aliased("max_damage_avatar", default=None)
    max_take_damage_character: typing.Optional[BattleStatCharacter] = Aliased("max_take_damage_avatar", default=None)
    fastest_character_list: typing.Sequence[BattleStatCharacter] = Aliased("shortest_avatar_list")
    total_cast_seconds: int = Aliased("total_use_time")


class ImgTheaterData(APIModel):
    """Imaginarium theater data."""

    acts: typing.Sequence[Act] = Aliased(alias="rounds_data")
    backup_characters: typing.Sequence[ActCharacter] = Aliased("backup_avatars")  # Not sure what this is
    stats: TheaterStats = Aliased(alias="stat")
    schedule: TheaterSchedule
    has_data: bool
    has_detail_data: bool
    battle_stats: typing.Optional[TheaterBattleStats] = Aliased("fight_statisic", default=None)

    @pydantic.model_validator(mode="before")
    def __unnest_detail(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        detail: typing.Optional[dict[str, typing.Any]] = values.get("detail")
        values["rounds_data"] = detail.get("rounds_data", []) if detail is not None else []
        values["backup_avatars"] = detail.get("backup_avatars", []) if detail is not None else []
        values["fight_statisic"] = detail.get("fight_statisic", None) if detail is not None else None
        return values


class ImgTheater(APIModel):
    """Imaginarium theater."""

    datas: typing.Sequence[ImgTheaterData] = Aliased("data")
    unlocked: bool = Aliased("is_unlock")
