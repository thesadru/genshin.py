import calendar
from datetime import datetime, timedelta, timezone
from typing import NamedTuple

from pydantic import Field

from .base import GenshinModel


class DailyRewardInfo(NamedTuple):
    """Information about the current daily reward status"""

    signed_in: bool
    claimed_rewards: int

    @property
    def missed_rewards(self):
        cn_timezone = timezone(timedelta(hours=8))
        now = datetime.now(cn_timezone)
        month_days = calendar.monthrange(now.year, now.month)[1]
        return month_days - self.claimed_rewards


class DailyReward(GenshinModel):
    """A claimable daily reward"""

    name: str
    amount: int = Field(galias="cnt")
    icon: str


class ClaimedDailyReward(GenshinModel):
    """A claimed daily reward"""

    id: int
    name: str
    amount: int = Field(galias="cnt")
    icon: str = Field(galias="img")
    time: datetime = Field(galias="created_at", timezone=8)
