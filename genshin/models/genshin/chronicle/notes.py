"""Genshin chronicle notes."""
import datetime
import typing

import pydantic

from genshin.models.genshin import character
from genshin.models.model import Aliased, APIModel

__all__ = ["Expedition", "ExpeditionCharacter", "Notes"]


def _process_timedelta(time: typing.Union[int, datetime.datetime]) -> datetime.datetime:
    if isinstance(time, int):
        time = datetime.datetime.fromtimestamp(time).astimezone()

    if time < datetime.datetime(2000, 1, 1).astimezone():
        delta = datetime.timedelta(seconds=int(time.timestamp()))
        time = datetime.datetime.now().astimezone() + delta

    return time


class ExpeditionCharacter(character.BaseCharacter):
    """Expedition character."""


class Expedition(APIModel):
    """Real-Time note expedition."""

    character: ExpeditionCharacter = Aliased("avatar_side_icon")
    status: typing.Literal["Ongoing", "Finished"]
    completion_time: datetime.datetime = Aliased("remained_time")

    @property
    def finished(self) -> bool:
        """Whether the expedition has finished."""
        return self.remaining_time == 0

    @property
    def remaining_time(self) -> float:
        """The remaining time until expedition completion in seconds."""
        remaining = self.completion_time - datetime.datetime.now().astimezone()
        return max(remaining.total_seconds(), 0)

    __fix_time = pydantic.validator("completion_time", allow_reuse=True)(_process_timedelta)

    @pydantic.validator("character", pre=True)
    def __complete_character(cls, v: typing.Any) -> ExpeditionCharacter:
        if isinstance(v, str):
            return ExpeditionCharacter(icon=v)  # type: ignore

        return v


class Notes(APIModel):
    """Real-Time notes."""

    current_resin: int
    max_resin: int
    resin_recovery_time: datetime.datetime = Aliased("resin_recovery_time")

    current_realm_currency: int = Aliased("current_home_coin")
    max_realm_currency: int = Aliased("max_home_coin")
    realm_currency_recovery_time: datetime.datetime = Aliased("home_coin_recovery_time")

    completed_commissions: int = Aliased("finished_task_num")
    max_commissions: int = Aliased("total_task_num")
    claimed_commission_reward: bool = Aliased("is_extra_task_reward_received")

    remaining_resin_discounts: int = Aliased("remain_resin_discount_num")
    max_resin_discounts: int = Aliased("resin_discount_num_limit")

    expeditions: typing.Sequence[Expedition]
    max_expeditions: int = Aliased("max_expedition_num")

    @property
    def remaining_resin_recovery_time(self) -> float:
        """The remaining time until resin recovery in seconds."""
        remaining = self.resin_recovery_time - datetime.datetime.now().astimezone()
        return max(remaining.total_seconds(), 0)

    @property
    def remaining_realm_currency_recovery_time(self) -> float:
        """The remaining time until realm currency recovery in seconds."""
        remaining = self.realm_currency_recovery_time - datetime.datetime.now().astimezone()
        return max(remaining.total_seconds(), 0)

    __fix_resin_time = pydantic.validator("resin_recovery_time", allow_reuse=True)(_process_timedelta)
    __fix_realm_time = pydantic.validator("realm_currency_recovery_time", allow_reuse=True)(_process_timedelta)
