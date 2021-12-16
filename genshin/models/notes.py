from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal

from pydantic import Field, root_validator, validator

from .base import BaseCharacter, GenshinModel

__all__ = ["Expedition", "Notes"]


class Expedition(GenshinModel):
    """A Real-Time note expedition"""

    character: BaseCharacter = Field(galias="avatar_side_icon")
    status: Literal["Ongoing", "Finished"]
    completed_at: datetime

    @property
    def finished(self) -> bool:
        """Whether the expedition has finished"""
        return self.remaining_time == 0

    @property
    def remaining_time(self) -> float:
        """The remaining time until expedition completion in seconds"""
        remaining = self.completed_at - datetime.now().astimezone()
        return max(remaining.total_seconds(), 0)

    @root_validator(pre=True)
    def __process_timedelta(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        time = timedelta(seconds=int(values["remained_time"]))
        values["completed_at"] = datetime.now().astimezone() + time

        return values

    @validator("character", pre=True)
    def __complete_character(cls, v: str) -> BaseCharacter:
        return BaseCharacter(icon=v)


class Notes(GenshinModel):
    """Real-Time notes"""

    current_resin: int
    max_resin: int
    resin_recovered_at: datetime

    completed_commissions: int = Field(galias="finished_task_num")
    max_comissions: int = Field(galias="total_task_num")
    claimed_comission_reward: bool = Field(galias="is_extra_task_reward_received")

    remaining_resin_discounts: int = Field(galias="remain_resin_discount_num")
    max_resin_discounts: int = Field(galias="resin_discount_num_limit")

    expeditions: List[Expedition]
    max_expeditions: int = Field(galias="max_expedition_num")

    @property
    def until_resin_recovery(self) -> float:
        """The remaining time until resin recovery in seconds"""
        remaining = self.resin_recovered_at - datetime.now().astimezone()
        return min(remaining.total_seconds(), 0)

    @root_validator(pre=True)
    def __process_timedelta(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        time = timedelta(seconds=int(values["resin_recovery_time"]))
        values["resin_recovered_at"] = datetime.now().astimezone() + time

        return values
