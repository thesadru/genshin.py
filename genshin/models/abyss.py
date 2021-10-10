from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import Field, root_validator

from .base import BaseCharacter, CharacterIcon, GenshinModel


class AbyssRankCharacter(BaseCharacter):
    """A character with a value of a rank"""

    id: int = Field(alias="avatar_id")
    icon: CharacterIcon = Field(alias="avatar_icon")

    value: int


class AbyssCharacter(BaseCharacter):
    """A character with just a level"""

    level: int


class CharacterRanks(GenshinModel):
    most_played: List[AbyssRankCharacter] = Field(alias="reveal_rank")
    most_kills: List[AbyssRankCharacter] = Field(alias="defeat_rank")
    strongest_strike: List[AbyssRankCharacter] = Field(alias="damage_rank")
    most_damage_taken: List[AbyssRankCharacter] = Field(alias="take_damage_rank")
    most_bursts_used: List[AbyssRankCharacter] = Field(alias="normal_skill_rank")
    most_skills_used: List[AbyssRankCharacter] = Field(alias="energy_skill_rank")

    def as_dict(self, lang: str = "en-us") -> Dict[str, Any]:
        """Helper function which turns fields into properly named ones"""
        assert lang == "en-us", "Other languages not yet implemented"

        return {key.replace("_", " ").title(): value for key, value in self.dict().items()}


class Battle(GenshinModel):
    half: int = Field(alias="index")
    timestamp: datetime
    characters: List[AbyssCharacter] = Field(alias="avatars")


class Chamber(GenshinModel):
    chamber: int = Field(alias="index")
    stars: int = Field(alias="star")
    max_stars: Literal[3] = Field(alias="max_star")
    battles: List[Battle]


class Floor(GenshinModel):
    floor: int = Field(alias="index")
    # icon: str - unused
    # settle_time: int - appsample might be using this?
    unlocked: Literal[True] = Field(alias="is_unlock")
    stars: int = Field(alias="star")
    max_stars: Literal[9] = Field(alias="max_star")  # maybe one day
    chambers: List[Chamber] = Field(alias="levels")


class SpiralAbyss(GenshinModel):
    unlocked: bool = Field(alias="is_unlock")
    season: int = Field(alias="schedule_id")
    start_time: datetime
    end_time: datetime

    total_battles: int = Field(alias="total_battle_times")
    total_wins: str = Field(alias="total_win_times")
    max_floor: str
    total_stars: int = Field(alias="total_star")

    ranks: CharacterRanks

    floors: List[Floor]

    @root_validator(pre=True)
    def __nest_ranks(cls, values: Dict[str, Any]):
        values["ranks"] = values
        return values
