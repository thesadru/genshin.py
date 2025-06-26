"""ZZZ sticky notes (real-time notes) models."""

import datetime
import enum
import logging
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, prevent_enum_error

__all__ = ("BatteryCharge", "VideoStoreState", "ZZZEngagement", "ZZZMemberCard", "ZZZNotes", "ZZZTempleRunning")

logger: logging.Logger = logging.getLogger(__name__)


class VideoStoreState(enum.Enum):
    """Video store management state."""

    REVENUE_AVAILABLE = "SaleStateDone"
    WAITING_TO_OPEN = "SaleStateNo"
    CURRENTLY_OPEN = "SaleStateDoing"


class BenchState(enum.Enum):
    """Bench management state."""

    CAN_PRODUCE = "BenchStateCanProduce"
    PRODUCING = "BenchStateProducing"
    UNKNOWN = "BenchStateUnknown"


class ShelveStoreState(enum.Enum):
    """Shelve management state."""

    CAN_SELL = "ShelveStateCanSell"
    SELLING = "ShelveStateSelling"
    SOLD_OUT = "ShelveStateSoldOut"
    UNKNOWN = "ShelveStateUnknown"


class ExpeditionState(enum.Enum):
    """Expedition state."""

    CAN_SEND = "ExpeditionStateInCanSend"
    IN_PROGRESS = "ExpeditionStateInProgress"
    ENDED = "ExpeditionStateEnd"
    UNKNOWN = "ExpeditionStateUnknown"


class ZZZMemberCardState(enum.Enum):
    """ZZZ Member Card state."""

    MEMBER = "MemberCardStateACK"
    NO = "MemberCardStateNo"


class ZZZCardSignState(enum.Enum):
    """ZZZ Member Card Sign state."""

    NO = "CardSignNo"
    DONE = "CardSignDone"


class BatteryCharge(APIModel):
    """ZZZ battery charge model."""

    current: int
    max: int
    seconds_till_full: int = Aliased("restore")

    @property
    def is_full(self) -> bool:
        """Check if the energy is full."""
        return self.current == self.max

    @property
    def full_datetime(self) -> datetime.datetime:
        """Get the datetime when the energy will be full."""
        return datetime.datetime.now().astimezone() + datetime.timedelta(seconds=self.seconds_till_full)

    @pydantic.model_validator(mode="before")
    @classmethod
    def __unnest_progress(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        return {**values, **values.pop("progress", {})}


class ZZZEngagement(APIModel):
    """ZZZ engagement model."""

    current: int
    max: int


class ZZZTempleRunning(APIModel):
    """ZZZ Suibian Temple Management model."""

    bench_state: typing.Union[BenchState, str]
    currency_next_refresh_ts: datetime.timedelta
    current_currency: int
    expedition_state: typing.Union[ExpeditionState, str]
    level: int
    shelve_state: typing.Union[ShelveStoreState, str]
    weekly_currency_max: int

    @property
    def reset_datetime(self) -> datetime.datetime:
        """The datetime when the currency will be reset."""
        return datetime.datetime.now().astimezone() + self.currency_next_refresh_ts

    @pydantic.field_validator("currency_next_refresh_ts", mode="before")
    @classmethod
    def __parse_currency_refresh(cls, v: str) -> datetime.timedelta:
        return datetime.timedelta(seconds=int(v))

    @pydantic.field_validator("bench_state", mode="before")
    @classmethod
    def __parse_bench_state(cls, v: str) -> typing.Union[BenchState, str]:
        return prevent_enum_error(v, BenchState)

    @pydantic.field_validator("expedition_state", mode="before")
    @classmethod
    def __parse_expedition_state(cls, v: str) -> typing.Union[ExpeditionState, str]:
        return prevent_enum_error(v, ExpeditionState)

    @pydantic.field_validator("shelve_state", mode="before")
    @classmethod
    def __parse_shelve_store_state(cls, v: str) -> typing.Union[ShelveStoreState, str]:
        return prevent_enum_error(v, ShelveStoreState)


class ZZZMemberCard(APIModel):
    """ZZZ Member Card model."""

    exp_time: datetime.timedelta
    is_open: bool
    member_card_state: ZZZMemberCardState

    @property
    def reset_datetime(self) -> datetime.datetime:
        """The datetime when the member card will be reset."""
        return datetime.datetime.now().astimezone() + self.exp_time

    @pydantic.field_validator("exp_time", mode="before")
    @classmethod
    def __parse_currency_refresh(cls, v: str) -> datetime.timedelta:
        return datetime.timedelta(seconds=int(v))


class BountyCommission(APIModel):
    """Bounty commission progress model."""

    cur_completed: int = Aliased("num")
    total: int
    refresh_time: datetime.timedelta

    @property
    def completed(self) -> bool:
        """Whether the bounty commissions are completed."""
        return self.cur_completed == self.total

    @property
    def reset_datetime(self) -> datetime.datetime:
        """The datetime when the bounty commission will be reset."""
        return datetime.datetime.now().astimezone() + self.refresh_time


class SurveyPoints(APIModel):
    """ZZZ sticky notes, Hollow Zero investigation points model."""

    num: int
    total: int
    is_max_level: bool  # Not sure what this means


class HollowZero(APIModel):
    """Hollow Zero in ZZZ sticky notes model."""

    bounty_commission: typing.Optional[BountyCommission] = None
    investigation_point: typing.Optional[SurveyPoints] = Aliased("survey_points", default=None)


class WeeklyTask(APIModel):
    """ZZZ sticky notes, Weekly task model."""

    cur_point: int
    max_point: int
    refresh_time: datetime.timedelta

    @property
    def completed(self) -> bool:
        """Whether the weekly tasks is full completed."""
        return self.cur_point >= self.max_point

    @property
    def reset_datetime(self) -> datetime.datetime:
        """The datetime when the weekly tasks will be reset."""
        return datetime.datetime.now().astimezone() + self.refresh_time


class ZZZNotes(APIModel):
    """Zenless Zone Zero sticky notes model."""

    battery_charge: BatteryCharge = Aliased("energy")
    engagement: ZZZEngagement = Aliased("vitality")
    scratch_card_completed: bool = Aliased("card_sign")
    video_store_state: VideoStoreState
    hollow_zero: HollowZero
    weekly_task: typing.Optional[WeeklyTask] = None
    card_sign: ZZZCardSignState
    member_card: ZZZMemberCard
    temple_running: ZZZTempleRunning

    @pydantic.field_validator("scratch_card_completed", mode="before")
    @classmethod
    def __transform_value(cls, v: typing.Literal["CardSignDone", "CardSignNotDone"]) -> bool:
        return v == "CardSignDone"

    @pydantic.model_validator(mode="before")
    @classmethod
    def __unnest_value(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if "video_store_state" not in values:
            values["video_store_state"] = values["vhs_sale"]["sale_state"]
        if "hollow_zero" not in values:
            values["hollow_zero"] = {
                "bounty_commission": values["bounty_commission"],
                "survey_points": values["survey_points"],
            }
        return values
