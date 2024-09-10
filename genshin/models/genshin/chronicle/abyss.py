import datetime
import typing

if typing.TYPE_CHECKING:
    import pydantic.v1 as pydantic
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
        import pydantic

from genshin.constants import CN_TIMEZONE
from genshin.models.genshin import character
from genshin.models.model import Aliased, APIModel

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

    id: int = Aliased("avatar_id")
    icon: str = Aliased("avatar_icon")

    value: int


class AbyssCharacter(character.BaseCharacter):
    """Character with just a level."""

    level: int


# flake8: noqa: E222
class CharacterRanks(APIModel):
    """Collection of rankings achieved during spiral abyss runs."""

    # fmt: off
    most_played: typing.Sequence[AbyssRankCharacter] =      Aliased("reveal_rank",       default=[], mi18n="bbs/go_fight_count")
    most_kills: typing.Sequence[AbyssRankCharacter] =       Aliased("defeat_rank",       default=[], mi18n="bbs/max_rout_count")
    strongest_strike: typing.Sequence[AbyssRankCharacter] = Aliased("damage_rank",       default=[], mi18n="bbs/powerful_attack")
    most_damage_taken: typing.Sequence[AbyssRankCharacter] = Aliased("take_damage_rank", default=[], mi18n="bbs/receive_max_damage")  # noqa: E501
    most_bursts_used: typing.Sequence[AbyssRankCharacter] = Aliased("energy_skill_rank", default=[], mi18n="bbs/element_break_count") # noqa: E501
    most_skills_used: typing.Sequence[AbyssRankCharacter] = Aliased("normal_skill_rank", default=[], mi18n="bbs/element_skill_use_count") # noqa: E501
    # fmt: on

    def as_dict(self, lang: str = "en-us") -> typing.Mapping[str, typing.Any]:
        """Turn fields into properly named ones."""
        return {
            self._get_mi18n(field, lang): getattr(self, field.name)
            for field in self.__fields__.values()
            if field.name != "lang"
        }


class Battle(APIModel):
    """Battle in the spiral abyss."""

    half: int = Aliased("index")
    timestamp: datetime.datetime
    characters: typing.Sequence[AbyssCharacter] = Aliased("avatars")


class Chamber(APIModel):
    """Chamber of the spiral abyss."""

    chamber: int = Aliased("index")
    stars: int = Aliased("star")
    max_stars: typing.Literal[3] = Aliased("max_star")
    battles: typing.Sequence[Battle]


class Floor(APIModel):
    """Floor of the spiral abyss."""

    floor: int = Aliased("index")
    # icon: str - unused
    # settle_time: int - appsample might be using this?
    unlocked: typing.Literal[True] = Aliased("is_unlock")
    stars: int = Aliased("star")
    max_stars: typing.Literal[9] = Aliased("max_star")  # maybe one day
    chambers: typing.Sequence[Chamber] = Aliased("levels")


class SpiralAbyss(APIModel):
    """Information about Spiral Abyss runs during a specific season."""

    unlocked: bool = Aliased("is_unlock")
    season: int = Aliased("schedule_id")
    start_time: datetime.datetime
    end_time: datetime.datetime

    total_battles: int = Aliased("total_battle_times")
    total_wins: str = Aliased("total_win_times")
    max_floor: str
    total_stars: int = Aliased("total_star")

    ranks: CharacterRanks

    floors: typing.Sequence[Floor]

    @pydantic.root_validator(pre=True)
    def __nest_ranks(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, AbyssCharacter]:
        """By default ranks are for some reason on the same level as the rest of the abyss."""
        values.setdefault("ranks", {}).update(values)
        return values

    @pydantic.validator("start_time", "end_time", pre=True)
    def __parse_timezones(cls, value: str) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(int(value), tz=CN_TIMEZONE)


class SpiralAbyssPair(APIModel):
    """Pair of both current and previous spiral abyss.

    This may not be a namedtuple due to how pydantic handles them.
    """

    current: SpiralAbyss
    previous: SpiralAbyss
