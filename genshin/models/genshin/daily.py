"""Daily reward models."""

import datetime
import typing

from genshin.constants import CN_TIMEZONE
from genshin.models.model import Aliased, APIModel, TZDateTime, Unique

__all__ = ["ClaimedDailyReward", "DailyReward", "DailyRewardInfo"]


class DailyRewardInfo(typing.NamedTuple):
    """Information about the current daily reward status."""

    signed_in: bool
    claimed_rewards: int

    @property
    def missed_rewards(self) -> int:
        now = datetime.datetime.now(CN_TIMEZONE)
        return now.day - self.claimed_rewards


class DailyReward(APIModel):
    """Claimable daily reward."""

    name: str
    amount: int = Aliased("cnt", default=0)
    icon: str


class ClaimedDailyReward(APIModel, Unique):
    """Claimed daily reward."""

    id: int
    name: str
    amount: int = Aliased("cnt")
    icon: str = Aliased("img")
    time: TZDateTime = Aliased("created_at")
