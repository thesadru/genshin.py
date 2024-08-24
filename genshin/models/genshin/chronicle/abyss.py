import datetime
import typing

import pydantic

from genshin.constants import CN_TIMEZONE
from genshin.models.genshin import character
from genshin.models.model import APIModel

__all__ = [
    "AbyssCharacter",
    "AbyssRankCharacter",
    "Battle",
    "Chamber",
    "CharacterRanks",
    "Floor",
    "SpiralAbyss",
    "SpiralAbyssPair",
]


class AbyssRankCharacter(character.BaseCharacter):
    """Character with a value of a rank."""

    id: int = pydantic.Field(alias="avatar_id")
    icon: str = pydantic.Field(alias="avatar_icon")

    value: int


class AbyssCharacter(character.BaseCharacter):
    """Character with just a level."""

    level: int


# flake8: noqa: E222
class CharacterRanks(APIModel):
    """Collection of rankings achieved during spiral abyss runs."""

    most_played: typing.Sequence[AbyssRankCharacter] = pydantic.Field(alias="reveal_rank", default=[])
    most_kills: typing.Sequence[AbyssRankCharacter] = pydantic.Field(alias="defeat_rank", default=[])
    strongest_strike: typing.Sequence[AbyssRankCharacter] = pydantic.Field(alias="damage_rank", default=[])
    most_damage_taken: typing.Sequence[AbyssRankCharacter] = pydantic.Field(alias="take_damage_rank", default=[])
    most_bursts_used: typing.Sequence[AbyssRankCharacter] = pydantic.Field(alias="energy_skill_rank", default=[])
    most_skills_used: typing.Sequence[AbyssRankCharacter] = pydantic.Field(alias="normal_skill_rank", default=[])


class Battle(APIModel):
    """Battle in the spiral abyss."""

    half: int = pydantic.Field(alias="index")
    timestamp: datetime.datetime
    characters: typing.Sequence[AbyssCharacter] = pydantic.Field(alias="avatars")


class Chamber(APIModel):
    """Chamber of the spiral abyss."""

    chamber: int = pydantic.Field(alias="index")
    stars: int = pydantic.Field(alias="star")
    max_stars: typing.Literal[3] = pydantic.Field(alias="max_star")
    battles: typing.Sequence[Battle]


class Floor(APIModel):
    """Floor of the spiral abyss."""

    floor: int = pydantic.Field(alias="index")
    # icon: str - unused
    # settle_time: int - appsample might be using this?
    unlocked: typing.Literal[True] = pydantic.Field(alias="is_unlock")
    stars: int = pydantic.Field(alias="star")
    max_stars: typing.Literal[9] = pydantic.Field(alias="max_star")  # maybe one day
    chambers: typing.Sequence[Chamber] = pydantic.Field(alias="levels")


class SpiralAbyss(APIModel):
    """Information about Spiral Abyss runs during a specific season."""

    unlocked: bool = pydantic.Field(alias="is_unlock")
    season: int = pydantic.Field(alias="schedule_id")
    start_time: datetime.datetime
    end_time: datetime.datetime

    total_battles: int = pydantic.Field(alias="total_battle_times")
    total_wins: str = pydantic.Field(alias="total_win_times")
    max_floor: str
    total_stars: int = pydantic.Field(alias="total_star")

    ranks: CharacterRanks

    floors: typing.Sequence[Floor]

    @pydantic.model_validator(mode="before")
    @classmethod
    def __nest_ranks(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, AbyssCharacter]:
        """By default ranks are for some reason on the same level as the rest of the abyss."""
        values.setdefault("ranks", {}).update(values)
        return values

    @pydantic.field_validator("start_time", "end_time", mode="before")
    @classmethod
    def __parse_timezones(cls, value: str) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(int(value), tz=CN_TIMEZONE)


class SpiralAbyssPair(APIModel):
    """Pair of both current and previous spiral abyss.

    This may not be a namedtuple due to how pydantic handles them.
    """

    current: SpiralAbyss
    previous: SpiralAbyss
