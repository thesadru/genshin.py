"""Starrail chronicle challenge."""

from typing import Any, Dict, List, Optional

import pydantic

from genshin.models.model import APIModel
from genshin.models.starrail.character import FloorCharacter

from .base import PartialTime

__all__ = [
    "APCShadowBoss",
    "APCShadowFloor",
    "APCShadowFloorNode",
    "APCShadowSeason",
    "ChallengeBuff",
    "FictionFloor",
    "FictionFloorNode",
    "FloorNode",
    "StarRailAPCShadow",
    "StarRailChallenge",
    "StarRailChallengeSeason",
    "StarRailFloor",
    "StarRailPureFiction",
]


class FloorNode(APIModel):
    """Node for a memory of chaos floor."""

    challenge_time: PartialTime
    avatars: List[FloorCharacter]


class StarRailChallengeFloor(APIModel):
    """Base model for star rail challenge floors."""

    id: int = pydantic.Field(alias="maze_id")
    name: str
    star_num: int
    is_quick_clear: bool = pydantic.Field(alias="is_fast")


class StarRailFloor(StarRailChallengeFloor):
    """Floor in a memory of chaos challenge."""

    round_num: int
    is_chaos: bool
    node_1: FloorNode
    node_2: FloorNode


class StarRailChallengeSeason(APIModel):
    """A season of a challenge."""

    id: int = pydantic.Field(alias="schedule_id")
    name: str = pydantic.Field(alias="name_mi18n")
    status: str
    begin_time: PartialTime
    end_time: PartialTime


class StarRailChallenge(APIModel):
    """Memory of chaos challenge in a season."""

    name: str
    season: int = pydantic.Field(alias="schedule_id")
    begin_time: PartialTime
    end_time: PartialTime

    total_stars: int = pydantic.Field(alias="star_num")
    max_floor: str
    total_battles: int = pydantic.Field(alias="battle_num")
    has_data: bool

    floors: List[StarRailFloor] = pydantic.Field(alias="all_floor_detail")
    seasons: List[StarRailChallengeSeason] = pydantic.Field(alias="groups")

    @pydantic.model_validator(mode="before")
    @classmethod
    def __extract_name(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "seasons" in values and isinstance(values["seasons"], List):
            seasons: List[Dict[str, Any]] = values["seasons"]
            if len(seasons) > 0:
                values["name"] = seasons[0]["name_mi18n"]

        return values


class ChallengeBuff(APIModel):
    """Buff used in a pure fiction or apocalyptic shadow node."""

    id: int
    name: str = pydantic.Field(alias="name_mi18n")
    description: str = pydantic.Field(alias="desc_mi18n")
    icon: str


class FictionFloorNode(FloorNode):
    """Node for a Pure Fiction floor."""

    buff: Optional[ChallengeBuff]
    score: int


class FictionFloor(StarRailChallengeFloor):
    """Floor in a Pure Fiction challenge."""

    round_num: int
    node_1: FictionFloorNode
    node_2: FictionFloorNode

    @property
    def score(self) -> int:
        """Total score of the floor."""
        return self.node_1.score + self.node_2.score


class StarRailPureFiction(APIModel):
    """Pure Fiction challenge in a season."""

    name: str = pydantic.Field(deprecated="Use `season_id` together with `seasons instead`.")
    season_id: int = pydantic.Field(deprecated="Use `season_id` together with `seasons instead`.")
    begin_time: PartialTime = pydantic.Field(deprecated="Use `season_id` together with `seasons instead`.")
    end_time: PartialTime = pydantic.Field(deprecated="Use `season_id` together with `seasons instead`.")

    total_stars: int = pydantic.Field(alias="star_num")
    max_floor: str
    total_battles: int = pydantic.Field(alias="battle_num")
    has_data: bool

    floors: List[FictionFloor] = pydantic.Field(alias="all_floor_detail")
    seasons: List[StarRailChallengeSeason] = pydantic.Field(alias="groups")
    max_floor_id: int

    @pydantic.model_validator(mode="before")
    @classmethod
    def __unnest_groups(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "seasons" in values and isinstance(values["seasons"], List):
            seasons: List[Dict[str, Any]] = values["seasons"]
            if len(seasons) > 0:
                values["name"] = seasons[0]["name_mi18n"]
                values["season_id"] = seasons[0]["schedule_id"]
                values["begin_time"] = seasons[0]["begin_time"]
                values["end_time"] = seasons[0]["end_time"]

        return values


class APCShadowFloorNode(FloorNode):
    """Node for a apocalyptic shadow floor."""

    challenge_time: Optional[PartialTime]  # type: ignore[assignment]
    buff: Optional[ChallengeBuff]
    score: int
    boss_defeated: bool

    @property
    def has_data(self) -> bool:
        """Check if the node has data."""
        return bool(self.avatars)


class APCShadowFloor(StarRailChallengeFloor):
    """Floor in an apocalyptic shadow challenge."""

    node_1: APCShadowFloorNode
    node_2: APCShadowFloorNode
    last_update_time: PartialTime

    @property
    def score(self) -> int:
        """Total score of the floor."""
        return self.node_1.score + self.node_2.score


class APCShadowBoss(APIModel):
    """Boss in an apocalyptic shadow challenge."""

    id: int
    name_mi18n: str
    icon: str


class APCShadowSeason(StarRailChallengeSeason):
    """Season of an apocalyptic shadow challenge."""

    upper_boss: APCShadowBoss
    lower_boss: APCShadowBoss


class StarRailAPCShadow(APIModel):
    """Apocalyptic shadow challenge in a season."""

    total_stars: int = pydantic.Field(alias="star_num")
    max_floor: str
    total_battles: int = pydantic.Field(alias="battle_num")
    has_data: bool

    floors: List[APCShadowFloor] = pydantic.Field(alias="all_floor_detail")
    seasons: List[APCShadowSeason] = pydantic.Field(alias="groups")
    max_floor_id: int
