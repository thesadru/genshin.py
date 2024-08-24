"""Daily reward models."""

import datetime
import typing

import pydantic

from genshin.constants import CN_TIMEZONE
from genshin.models.model import APIModel, UTC8Timestamp

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
    amount: int = pydantic.Field(alias="cnt")
    icon: str


class ClaimedDailyReward(APIModel):
    """Claimed daily reward."""

    id: int
    name: str
    amount: int = pydantic.Field(alias="cnt")
    icon: str = pydantic.Field(alias="img")
    time: UTC8Timestamp = pydantic.Field(alias="created_at")
