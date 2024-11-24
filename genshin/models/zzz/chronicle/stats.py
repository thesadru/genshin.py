"""ZZZ data overview models."""

import typing

import pydantic

from genshin.models.model import Aliased, APIModel

from ..character import ZZZPartialAgent

__all__ = (
    "HIACoin",
    "ZZZBaseBangboo",
    "ZZZStats",
    "ZZZUserStats",
)


class HIACoin(APIModel):
    """HIACoin model."""

    num: int
    name: str
    icon: str = Aliased("url")


class ZZZStats(APIModel):
    """ZZZ data overview stats."""

    active_days: int
    character_num: int = Aliased("avatar_num")
    inter_knot_reputation: str = Aliased("world_level_name")
    shiyu_defense_frontiers: int = Aliased("cur_period_zone_layer_count")
    bangboo_obtained: int = Aliased("buddy_num")
    achievement_count: int
    hia_coin: HIACoin = Aliased("commemorative_coins_list")

    @pydantic.field_validator("hia_coin", mode="before")
    def __unnest_hia_coin(cls, v: typing.List[typing.Dict[str, typing.Any]]) -> typing.Dict[str, typing.Any]:
        return v[0]


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
    in_game_avatar: str = Aliased("cur_head_icon_url")
