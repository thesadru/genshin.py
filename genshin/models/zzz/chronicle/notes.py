"""ZZZ sticky notes (real-time notes) models."""

import datetime
import enum
import typing

import pydantic

from genshin.models.model import Aliased, APIModel

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
    def __unnest_progress(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        return {**values, **values.pop("progress")}


class ZZZEngagement(APIModel):
    """ZZZ engagement model."""

    current: int
    max: int


class BountyCommission(APIModel):
    """ZZZ sticky notes, Hollow Zero bounty commission model."""

    num: int
    total: int


class SurveyPoints(APIModel):
    """ZZZ sticky notes, Hollow Zero investigation points model."""

    num: int
    total: int
    is_max_level: bool  # Not sure what this means


class HollowZero(APIModel):
    """Hollow Zero in ZZZ sticky notes model."""

    bounty_commission: typing.Optional[BountyCommission] = None
    investigation_point: typing.Optional[SurveyPoints] = Aliased("survey_points", default=None)


class ZZZNotes(APIModel):
    """Zenless Zone Zero sticky notes model."""

    battery_charge: BatteryCharge = Aliased("energy")
    engagement: ZZZEngagement = Aliased("vitality")
    scratch_card_completed: bool = Aliased("card_sign")
    video_store_state: VideoStoreState
    hollow_zero: HollowZero

    @pydantic.field_validator("scratch_card_completed", mode="before")
    def __transform_value(cls, v: typing.Literal["CardSignDone", "CardSignNotDone"]) -> bool:
        return v == "CardSignDone"

    @pydantic.model_validator(mode="before")
    def __unnest_value(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if "video_store_state" not in values:
            values["video_store_state"] = values["vhs_sale"]["sale_state"]
        if "hollow_zero" not in values:
            values["hollow_zero"] = {
                "bounty_commission": values["bounty_commission"],
                "survey_points": values["survey_points"],
            }
        return values
