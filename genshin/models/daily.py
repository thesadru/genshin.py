from datetime import datetime
from typing import NamedTuple

from pydantic import Field

from .base import GenshinModel


class DailyRewardInfo(NamedTuple):
    """Information about the current daily reward status"""

    signed_in: bool
    claimed_rewards: int


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
