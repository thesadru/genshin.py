"""Genshin chronicle notes."""
import datetime
import typing

import pydantic

from genshin.models.genshin import character
from genshin.models.model import Aliased, APIModel

__all__ = ["Expedition", "Notes"]


class ExpeditionCharacter(character.BaseCharacter):
    """Expedition character."""


class Expedition(APIModel):
    """Real-Time note expedition."""

    character: ExpeditionCharacter = Aliased("avatar_side_icon")
    status: typing.Literal["Ongoing", "Finished"]
    completed_at: datetime.datetime

    @property
    def finished(self) -> bool:
        """Whether the expedition has finished"""
        return self.remaining_time == 0

    @property
    def remaining_time(self) -> float:
        """The remaining time until expedition completion in seconds"""
        remaining = self.completed_at - datetime.datetime.now().astimezone()
        return max(remaining.total_seconds(), 0)

    @pydantic.root_validator(pre=True)
    def __process_timedelta(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        time = datetime.timedelta(seconds=int(values["remained_time"]))
        values["completed_at"] = datetime.datetime.now().astimezone() + time

        return values

    @pydantic.validator("character", pre=True)
    def __complete_character(cls, v: str) -> ExpeditionCharacter:
        return ExpeditionCharacter(icon=v)  # type: ignore


class Notes(APIModel):
    """Real-Time notes."""

    current_resin: int
    max_resin: int
    resin_recovered_at: datetime.datetime

    current_realm_currency: int = Aliased("current_home_coin")
    max_realm_currency: int = Aliased("max_home_coin")
    realm_currency_recovered_at: datetime.datetime = Aliased("home_coin_recovery_time")

    completed_commissions: int = Aliased("finished_task_num")
    max_comissions: int = Aliased("total_task_num")
    claimed_comission_reward: bool = Aliased("is_extra_task_reward_received")

    remaining_resin_discounts: int = Aliased("remain_resin_discount_num")
    max_resin_discounts: int = Aliased("resin_discount_num_limit")

    expeditions: typing.Sequence[Expedition]
    max_expeditions: int = Aliased("max_expedition_num")

    @property
    def until_resin_recovery(self) -> float:
        """The remaining time until resin recovery in seconds"""
        remaining = self.resin_recovered_at - datetime.datetime.now().astimezone()
        return min(remaining.total_seconds(), 0)

    @property
    def until_realm_currency_recovery(self) -> float:
        """The remaining time until resin recovery in seconds"""
        remaining = self.realm_currency_recovered_at - datetime.datetime.now().astimezone()
        return max(remaining.total_seconds(), 0)

    @pydantic.root_validator(pre=True)
    def __process_timedelta(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        time = datetime.timedelta(seconds=int(values["resin_recovery_time"]))
        values["resin_recovered_at"] = datetime.datetime.now().astimezone() + time

        return values
