"""Starrail chronicle challenge."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    import pydantic.v1 as pydantic
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
        import pydantic

from genshin.models.model import Aliased, APIModel
from genshin.models.starrail.character import FloorCharacter

from .base import PartialTime

__all__ = [
    "FictionBuff",
    "FictionFloor",
    "FictionFloorNode",
    "FloorNode",
    "StarRailChallenge",
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

    name: str
    season_id: int
    begin_time: PartialTime
    end_time: PartialTime

    total_stars: int = Aliased("star_num")
    max_floor: str
    total_battles: int = Aliased("battle_num")
    has_data: bool

    floors: List[FictionFloor] = Aliased("all_floor_detail")
    max_floor_id: int

    @pydantic.root_validator(pre=True)
    def __unnest_groups(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "groups" in values and isinstance(values["groups"], List):
            groups: List[Dict[str, Any]] = values["groups"]
            if len(groups) > 0:
                values["name"] = groups[0]["name_mi18n"]
                values["season_id"] = groups[0]["schedule_id"]
                values["begin_time"] = groups[0]["begin_time"]
                values["end_time"] = groups[0]["end_time"]

        return values
