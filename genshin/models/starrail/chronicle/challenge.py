"""Starrail chronicle challenge."""
import datetime
from typing import List

from genshin.models.model import APIModel, Aliased

__all__ = ["ChallengeTime", "FloorCharacter", "FloorNode", "Floor", "Challenge"]


class ChallengeTime(APIModel):
    """Time of a challenge."""

    year: int
    month: int
    day: int
    hour: int
    minute: int

    @property
    def datetime(self):
        return datetime.datetime(self.year, self.month, self.day, self.hour, self.minute)


class FloorCharacter(APIModel):
    """Character in a floor."""

    id: int
    level: int
    icon: str
    rarity: int
    element: str


class FloorNode(APIModel):
    """Node for a floor."""

    challenge_time: ChallengeTime
    avatars: List[FloorCharacter]


class Floor(APIModel):
    """Floor in a challenge."""

    name: str
    round_num: int
    star_num: int
    node_1: FloorNode
    node_2: FloorNode
    is_chaos: bool


class Challenge(APIModel):
    """Challenge in a season."""

    season: int = Aliased("schedule_id")
    begin_time: ChallengeTime
    end_time: ChallengeTime

    total_stars: int = Aliased("star_num")
    max_floor: str
    total_battles: int = Aliased("battle_num")
    has_data: bool

    floors: List[Floor] = Aliased("all_floor_detail")
