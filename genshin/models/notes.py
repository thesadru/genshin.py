from datetime import datetime, timedelta
from typing import Any, Dict, List

from pydantic import Field, root_validator, validator

from .base import BaseCharacter, GenshinModel


class Expedition(GenshinModel):
    """A Real-Time note expedition"""

    character: BaseCharacter = Field(galias="avatar_side_icon")
    status: str
    completed_at: datetime

    @property
    def remaining(self) -> timedelta:
        return self.completed_at - datetime.now().astimezone()

    @root_validator(pre=True)
    def __process_timedelta(cls, values: Dict[str, Any]):
        time = timedelta(seconds=int(values["remained_time"]))
        values["completed_at"] = datetime.now().astimezone() + time

        return values

    @validator("character", pre=True)
    def __complete_character(cls, v):
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

    @root_validator(pre=True)
    def __process_timedelta(cls, values: Dict[str, Any]):
        time = timedelta(seconds=int(values["resin_recovery_time"]))
        values["resin_recovered_at"] = datetime.now().astimezone() + time

        return values
