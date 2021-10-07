from datetime import datetime
from typing import NamedTuple

from pydantic import BaseModel, Field


class DailyRewardInfo(NamedTuple):
    signed_in: bool
    claimed_rewards: int

class DailyReward(BaseModel):
    name: str
    amount: int = Field(alias="cnt")
    icon: str

class ClaimedDailyReward(BaseModel):
    id: int
    name: str
    amount: int = Field(alias="cnt")
    icon: str = Field(alias="img")
    time: datetime = Field(alias="created_at")
