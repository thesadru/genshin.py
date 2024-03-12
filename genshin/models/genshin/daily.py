"""Daily reward models."""

import datetime
import typing

from genshin.models.model import Aliased, APIModel, Unique

__all__ = ["ClaimedDailyReward", "DailyReward", "DailyRewardInfo"]


class DailyRewardInfo(typing.NamedTuple):
    """Information about the current daily reward status."""

    signed_in: bool
    claimed_rewards: int
    missed_rewards: int


class DailyReward(APIModel):
    """Claimable daily reward."""

    name: str
    amount: int = Aliased("cnt")
    icon: str


class ClaimedDailyReward(APIModel, Unique):
    """Claimed daily reward."""

    id: int
    name: str
    amount: int = Aliased("cnt")
    icon: str = Aliased("img")
    time: datetime.datetime = Aliased("created_at", timezone=8)
