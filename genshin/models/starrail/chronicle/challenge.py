"""Starrail chronicle challenge."""

import typing

import pydantic

from genshin.models.model import Aliased, APIModel
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
    avatars: list[FloorCharacter]


class StarRailChallengeFloor(APIModel):
    """Base model for star rail challenge floors."""

    id: int = Aliased("maze_id")
    name: str
    star_num: int
    is_quick_clear: bool = Aliased("is_fast")


class StarRailFloor(StarRailChallengeFloor):
    """Floor in a memory of chaos challenge."""

    round_num: int
    is_chaos: bool
    node_1: FloorNode
    node_2: FloorNode


class StarRailChallengeSeason(APIModel):
    """A season of a challenge."""

    id: int = Aliased("schedule_id")
    name: str = Aliased("name_mi18n")
    status: str
    begin_time: PartialTime
    end_time: PartialTime


class StarRailChallenge(APIModel):
    """Memory of chaos challenge in a season."""

    name: str
    season: int = Aliased("schedule_id")
    begin_time: typing.Optional[PartialTime]
    end_time: typing.Optional[PartialTime]

    total_stars: int = Aliased("star_num")
    max_floor: str
    total_battles: int = Aliased("battle_num")
    has_data: bool

    floors: typing.Sequence[StarRailFloor] = Aliased("all_floor_detail")
    seasons: typing.Sequence[StarRailChallengeSeason] = Aliased("groups")

    @pydantic.model_validator(mode="before")
    def __extract_name(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if "groups" in values and isinstance(values["groups"], list):
            seasons = typing.cast(list[dict[str, typing.Any]], values["groups"])
            if len(seasons) > 0:
                values["name"] = seasons[0]["name_mi18n"]
            else:
                values["name"] = ""

        return values


class ChallengeBuff(APIModel):
    """Buff used in a pure fiction or apocalyptic shadow node."""

    id: int
    name: str = Aliased("name_mi18n")
    description: str = Aliased("desc_mi18n")
    icon: str


class FictionFloorNode(FloorNode):
    """Node for a Pure Fiction floor."""

    buff: typing.Optional[ChallengeBuff]
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

    total_stars: int = Aliased("star_num")
    max_floor: str
    total_battles: int = Aliased("battle_num")
    has_data: bool

    floors: list[FictionFloor] = Aliased("all_floor_detail")
    seasons: list[StarRailChallengeSeason] = Aliased("groups")
    max_floor_id: int

    @pydantic.model_validator(mode="before")
    def __unnest_groups(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if "groups" in values and isinstance(values["groups"], list):
            seasons = typing.cast(list[dict[str, typing.Any]], values["groups"])
            if len(seasons) > 0:
                values["name"] = seasons[0]["name_mi18n"]
                values["season_id"] = seasons[0]["schedule_id"]
                values["begin_time"] = seasons[0]["begin_time"]
                values["end_time"] = seasons[0]["end_time"]

        return values


class APCShadowFloorNode(FloorNode):
    """Node for a apocalyptic shadow floor."""

    challenge_time: typing.Optional[PartialTime]  # type: ignore[assignment]
    buff: typing.Optional[ChallengeBuff]
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
    is_quick_clear: bool = Aliased("is_fast")

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

    total_stars: int = Aliased("star_num")
    max_floor: str
    total_battles: int = Aliased("battle_num")
    has_data: bool

    floors: list[APCShadowFloor] = Aliased("all_floor_detail")
    seasons: list[APCShadowSeason] = Aliased("groups")
    max_floor_id: int
