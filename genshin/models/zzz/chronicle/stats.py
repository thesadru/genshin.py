"""ZZZ data overview models."""

import typing

import pydantic

from genshin.models.model import APIModel
from genshin.models.zzz.character import ZZZPartialAgent

__all__ = (
    "ZZZBaseBangboo",
    "ZZZStats",
    "ZZZUserStats",
)


class ZZZStats(APIModel):
    """ZZZ data overview stats."""

    active_days: int
    character_num: int = pydantic.Field(alias="avatar_num")
    inter_knot_reputation: str = pydantic.Field(alias="world_level_name")
    shiyu_defense_frontiers: int = pydantic.Field(alias="cur_period_zone_layer_count")
    bangboo_obtained: int = pydantic.Field(alias="buddy_num")


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
    agents: typing.Sequence[ZZZPartialAgent] = pydantic.Field(alias="avatar_list")
    bangboos: typing.Sequence[ZZZBaseBangboo] = pydantic.Field(alias="buddy_list")
