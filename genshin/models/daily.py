from datetime import datetime
from typing import NamedTuple

from pydantic import Field

from .base import GenshinModel


class DailyRewardInfo(NamedTuple):
    signed_in: bool
    claimed_rewards: int


class DailyReward(GenshinModel):
    name: str
    amount: int = Field(alias="cnt")
    icon: str


class ClaimedDailyReward(GenshinModel):
    id: int
    name: str
    amount: int = Field(alias="cnt")
    icon: str = Field(alias="img")
    time: datetime = Field(alias="created_at")
