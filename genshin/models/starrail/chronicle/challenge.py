"""Starrail chronicle challenge."""
from typing import List

from genshin.models.model import Aliased, APIModel
from genshin.models.starrail.character import FloorCharacter

from .base import PartialTime

__all__ = ["StarRailFloor", "FloorNode", "StarRailChallenge"]


class FloorNode(APIModel):
    """Node for a floor."""

    challenge_time: PartialTime
    avatars: List[FloorCharacter]


class StarRailFloor(APIModel):
    """Floor in a challenge."""

    name: str
    round_num: int
    star_num: int
    node_1: FloorNode
    node_2: FloorNode
    is_chaos: bool


class StarRailChallenge(APIModel):
    """Challenge in a season."""

    season: int = Aliased("schedule_id")
    begin_time: PartialTime
    end_time: PartialTime

    total_stars: int = Aliased("star_num")
    max_floor: str
    total_battles: int = Aliased("battle_num")
    has_data: bool

    floors: List[StarRailFloor] = Aliased("all_floor_detail")
