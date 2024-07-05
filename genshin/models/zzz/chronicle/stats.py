"""ZZZ data overview models."""

import typing

from genshin.models.model import Aliased, APIModel

from ..character import ZZZPartialAgent

__all__ = (
    "ZZZStats",
    "ZZZUserStats",
)


class ZZZStats(APIModel):
    """ZZZ data overview stats."""

    active_days: int
    character_num: int = Aliased("avatar_num")
    inter_knot_reputation: str = Aliased("world_level_name")
    shiyu_defense_frontiers: int = Aliased("cur_period_zone_layer_count")
    bangboo_obtained: int = Aliased("buddy_num")


class ZZZBaseBangboo(APIModel):
    """Base bangboo (buddy) model."""

    id: int
    name: str
    rarity: typing.Literal["S", "A"]
    level: int
    star: int


class ZZZUserStats(APIModel):
    """Zenless Zone Zero user model."""

    stats: ZZZStats
    agents: typing.Sequence[ZZZPartialAgent] = Aliased("avatar_list")
    bangboos: typing.Sequence[ZZZBaseBangboo] = Aliased("buddy_list")
