"""Starrail chronicle challenge."""

from typing import List, Optional

from genshin.models.model import Aliased, APIModel
from genshin.models.starrail.character import FloorCharacter

from .base import PartialTime

__all__ = [
    "FictionBuff",
    "FictionFloor",
    "FictionFloorNode",
    "FloorNode",
    "StarRailChallenge",
    "StarRailChallengeSeason",
    "StarRailFloor",
    "StarRailPureFiction",
]


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


class StarRailChallengeSeason(APIModel):
    """A season of a challenge."""

    id: int = Aliased("schedule_id")
    name: str = Aliased("name_mi18n")
    status: str
    begin_time: PartialTime
    end_time: PartialTime


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
    seasons: List[StarRailChallengeSeason] = Aliased("groups")


class FictionBuff(APIModel):
    """Buff for a Pure Fiction floor."""

    id: int
    name: str = Aliased("name_mi18n")
    description: str = Aliased("desc_mi18n")
    icon: str


class FictionFloorNode(FloorNode):
    """Node for a Pure Fiction floor."""

    buff: Optional[FictionBuff]
    score: int


class FictionFloor(APIModel):
    """Floor in a Pure Fiction challenge."""

    id: int = Aliased("maze_id")
    name: str
    round_num: int
    star_num: int
    node_1: FictionFloorNode
    node_2: FictionFloorNode
    is_fast: bool

    @property
    def score(self) -> int:
        """Total score of the floor."""
        return self.node_1.score + self.node_2.score


class StarRailPureFiction(APIModel):
    """Pure Fiction challenge in a season."""

    total_stars: int = Aliased("star_num")
    max_floor: str
    total_battles: int = Aliased("battle_num")
    has_data: bool

    floors: List[FictionFloor] = Aliased("all_floor_detail")
    seasons: List[StarRailChallengeSeason] = Aliased("groups")
    max_floor_id: int
