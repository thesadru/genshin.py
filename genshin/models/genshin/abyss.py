from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import Field, root_validator

from ..base import BaseCharacter, APIModel

__all__ = [
    "AbyssRankCharacter",
    "AbyssCharacter",
    "CharacterRanks",
    "Battle",
    "Chamber",
    "Floor",
    "SpiralAbyss",
    "SpiralAbyssPair",
]


class AbyssRankCharacter(BaseCharacter):
    """A character with a value of a rank"""

    id: int = Field(galias="avatar_id")
    icon: str = Field(galias="avatar_icon")

    value: int


class AbyssCharacter(BaseCharacter):
    """A character with just a level"""

    level: int


class CharacterRanks(APIModel):
    """A collection of rankings achieved during spiral abyss runs"""

    # fmt: off
    most_played: List[AbyssRankCharacter] = Field([],      galias="reveal_rank",       mi18n="bbs/go_fight_count")
    most_kills: List[AbyssRankCharacter] = Field([],       galias="defeat_rank",       mi18n="bbs/max_rout_count")
    strongest_strike: List[AbyssRankCharacter] = Field([], galias="damage_rank",       mi18n="bbs/powerful_attack")
    most_damage_taken: List[AbyssRankCharacter] = Field([],galias="take_damage_rank",  mi18n="bbs/receive_max_damage")
    most_bursts_used: List[AbyssRankCharacter] = Field([], galias="energy_skill_rank", mi18n="bbs/element_break_count")
    most_skills_used: List[AbyssRankCharacter] = Field([], galias="normal_skill_rank", mi18n="bbs/element_skill_use_count")
    # fmt: on

    def as_dict(self, lang: str = "en-us") -> Dict[str, Any]:
        """Helper function which turns fields into properly named ones"""
        return {
            self._get_mi18n(field, lang): getattr(self, field.name)
            for field in self.__fields__.values()
        }


class Battle(APIModel):
    """A battle in the spiral abyss"""

    half: int = Field(galias="index")
    timestamp: datetime
    characters: List[AbyssCharacter] = Field(galias="avatars")


class Chamber(APIModel):
    """A chamber of the spiral abyss"""

    chamber: int = Field(galias="index")
    stars: int = Field(galias="star")
    max_stars: Literal[3] = Field(galias="max_star")
    battles: List[Battle]


class Floor(APIModel):
    """A floor of the spiral abyss"""

    floor: int = Field(galias="index")
    # icon: str - unused
    # settle_time: int - appsample might be using this?
    unlocked: Literal[True] = Field(galias="is_unlock")
    stars: int = Field(galias="star")
    max_stars: Literal[9] = Field(galias="max_star")  # maybe one day
    chambers: List[Chamber] = Field(galias="levels")


class SpiralAbyss(APIModel):
    """Information about Spiral Abyss runs during a specific season"""

    unlocked: bool = Field(galias="is_unlock")
    season: int = Field(galias="schedule_id")
    start_time: datetime
    end_time: datetime

    total_battles: int = Field(galias="total_battle_times")
    total_wins: str = Field(galias="total_win_times")
    max_floor: str
    total_stars: int = Field(galias="total_star")

    ranks: CharacterRanks

    floors: List[Floor]

    @root_validator(pre=True)
    def __nest_ranks(cls, values: Dict[str, Any]) -> Dict[str, AbyssCharacter]:
        """By default ranks are for some reason on the same level as the rest of the abyss"""
        values.setdefault("ranks", {}).update(values)
        return values


class SpiralAbyssPair(APIModel):
    """A pair of both current and previous spiral abyss

    This may not be a namedtuple due to how pydantic handles them
    """

    current: SpiralAbyss
    previous: SpiralAbyss
