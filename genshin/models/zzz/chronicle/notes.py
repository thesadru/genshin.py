"""ZZZ sticky notes (real-time notes) models."""

import datetime
import enum
import typing

import pydantic

from genshin.models.model import APIModel

__all__ = ("BatteryCharge", "VideoStoreState", "ZZZEngagement", "ZZZNotes")


class VideoStoreState(enum.Enum):
    """Video store management state."""

    REVENUE_AVAILABLE = "SaleStateDone"
    WAITING_TO_OPEN = "SaleStateNo"
    CURRENTLY_OPEN = "SaleStateDoing"


class BatteryCharge(APIModel):
    """ZZZ battery charge model."""

    current: int
    max: int
    seconds_till_full: int = pydantic.Field(alias="restore")

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
    def __unnest_progress(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        return {**values, **values.pop("progress")}


class ZZZEngagement(APIModel):
    """ZZZ engagement model."""

    current: int
    max: int


class ZZZNotes(APIModel):
    """Zenless Zone Zero sticky notes model."""

    battery_charge: BatteryCharge = pydantic.Field(alias="energy")
    engagement: ZZZEngagement = pydantic.Field(alias="vitality")
    scratch_card_completed: bool = pydantic.Field(alias="card_sign")
    video_store_state: VideoStoreState

    @pydantic.field_validator("scratch_card_completed", mode="before")
    @classmethod
    def __transform_value(cls, v: typing.Literal["CardSignDone", "CardSignNotDone"]) -> bool:
        return v == "CardSignDone"

    @pydantic.model_validator(mode="before")
    @classmethod
    def __unnest_value(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        values["video_store_state"] = values["vhs_sale"]["sale_state"]
        return values
