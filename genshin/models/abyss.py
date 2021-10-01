from typing import Any, Dict, List, Literal
import re
from pydantic import BaseModel, Field, root_validator, validator
from datetime import datetime

from .base import BaseCharacter


class AbyssRankCharacter(BaseCharacter):
    """A character with a value of a rank"""
    id: int = Field(alias="avatar_id")
    icon: str = Field(alias="avatar_icon")
    
    value: int


class AbyssCharacter(BaseCharacter):
    """A character with just a level"""
    level: int


class CharacterRanks(BaseModel):
    most_played: List[AbyssRankCharacter] = Field(alias="reveal_rank")
    most_kills: List[AbyssRankCharacter] = Field(alias="defeat_rank")
    strongest_strike: List[AbyssRankCharacter] = Field(alias="damage_rank")
    most_damage_taken: List[AbyssRankCharacter] = Field(alias="take_damage_rank")
    most_bursts_used: List[AbyssRankCharacter] = Field(alias="normal_skill_rank")
    most_skills_used: List[AbyssRankCharacter] = Field(alias="energy_skill_rank")


class Battle(BaseModel):
    half: int = Field(alias="index")
    timestamp: datetime
    characters: List[AbyssCharacter] = Field(alias="avatars")


class Chamber(BaseModel):
    chamber: int = Field(alias="index")
    stars: int = Field(alias="star")
    max_stars: Literal[3] = Field(alias="max_star")
    battles: List[Battle]


class Floor(BaseModel):
    floor: int = Field(alias="index")
    # icon: str - unused
    # settle_time: int - appsample might be using this?
    unlocked: Literal[True] = Field(alias="is_unlock")
    stars: int = Field(alias="star")
    max_stars: Literal[9] = Field(alias="max_star")  # maybe one day
    chambers: List[Chamber] = Field(alias="levels")


class SpiralAbyss(BaseModel):
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
