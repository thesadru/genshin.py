import datetime
import enum
import typing

import pydantic

from genshin.constants import CN_TIMEZONE
from genshin.models.genshin import character
from genshin.models.model import APIModel

__all__ = (
    "Act",
    "ActCharacter",
    "ImgTheater",
    "ImgTheaterData",
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


class ActCharacter(character.BaseCharacter):
    """A character in an act."""

    type: TheaterCharaType = pydantic.Field(alias="avatar_type")
    level: int


class TheaterBuff(APIModel):
    """Represents either a 'mystery cache' or a 'wondrous boom'."""

    icon: str
    name: str
    description: str = pydantic.Field(alias="desc")
    received_audience_support: bool = pydantic.Field(alias="is_enhanced")
    """Whether external audience support is received."""
    id: int


class Act(APIModel):
    """One act in the theater."""

    characters: typing.Sequence[ActCharacter] = pydantic.Field(alias="avatars")
    mystery_caches: typing.Sequence[TheaterBuff] = pydantic.Field(alias="choice_cards")
    wondroud_booms: typing.Sequence[TheaterBuff] = pydantic.Field(alias="buffs")
    medal_obtained: bool = pydantic.Field(alias="is_get_medal")
    round_id: int
    finish_time: int  # As timestamp
    finish_datetime: datetime.datetime = pydantic.Field(alias="finish_date_time")

    @pydantic.field_validator("finish_datetime", mode="before")
    @classmethod
    def __parse_datetime(cls, value: typing.Mapping[str, typing.Any]) -> datetime.datetime:
        return datetime.datetime(
            year=value["year"],
            month=value["month"],
            day=value["day"],
            hour=value["hour"],
            minute=value["minute"],
            second=value["second"],
            tzinfo=CN_TIMEZONE,
        )


class TheaterStats(APIModel):
    """Imaginarium theater stats."""

    difficulty: TheaterDifficulty = pydantic.Field(alias="difficulty_id")
    best_record: int = pydantic.Field(alias="max_round_id")
    """The maximum act the player has reached."""
    heraldry: int  # Not sure what this is
    star_challenge_stellas: typing.Sequence[bool] = pydantic.Field(alias="get_medal_round_list")
    """Whether the player has obtained the medal for each act."""
    fantasia_flowers_used: int = pydantic.Field(alias="coin_num")
    """The number of Fantasia Flowers used."""
    audience_support_trigger_num: int = pydantic.Field(alias="avatar_bonus_num")
    """The number of external audience support triggers."""
    player_assists: int = pydantic.Field(alias="rent_cnt")
    """The number of supporting cast characters assisting other players."""
    medal_num: int
    """The number of medals the player has obtained."""


class TheaterSchedule(APIModel):
    """Imaginarium theater schedule."""

    start_time: int  # As timestamp
    end_time: int  # As timestamp
    schedule_type: int  # Not sure what this is
    id: int = pydantic.Field(alias="schedule_id")
    start_datetime: datetime.datetime = pydantic.Field(alias="start_date_time")
    end_datetime: datetime.datetime = pydantic.Field(alias="end_date_time")

    @pydantic.field_validator("start_datetime", "end_datetime", mode="before")
    @classmethod
    def __parse_datetime(cls, value: typing.Mapping[str, typing.Any]) -> datetime.datetime:
        return datetime.datetime(
            year=value["year"],
            month=value["month"],
            day=value["day"],
            hour=value["hour"],
            minute=value["minute"],
            second=value["second"],
            tzinfo=CN_TIMEZONE,
        )


class ImgTheaterData(APIModel):
    """Imaginarium theater data."""

    acts: typing.Sequence[Act] = pydantic.Field(alias="rounds_data")
    backup_characters: typing.Sequence[ActCharacter] = pydantic.Field(alias="backup_avatars")  # Not sure what this is
    stats: TheaterStats = pydantic.Field(alias="stat")
    schedule: TheaterSchedule
    has_data: bool
    has_detail_data: bool

    @pydantic.model_validator(mode="before")
    @classmethod
    def __unnest_detail(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        detail: typing.Optional[typing.Dict[str, typing.Any]] = values.get("detail")
        values["rounds_data"] = detail.get("rounds_data", []) if detail is not None else []
        values["backup_avatars"] = detail.get("backup_avatars", []) if detail is not None else []
        return values


class ImgTheater(APIModel):
    """Imaginarium theater."""

    datas: typing.Sequence[ImgTheaterData] = pydantic.Field(alias="data")
    unlocked: bool = pydantic.Field(alias="is_unlock")
