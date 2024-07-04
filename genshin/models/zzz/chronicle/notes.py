"""ZZZ sticky notes (real-time notes) models."""

import datetime
import enum
import typing

from genshin.models.model import Aliased, APIModel

if typing.TYPE_CHECKING:
    import pydantic.v1 as pydantic
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
        import pydantic

__all__ = ("ZZZNotes", "VideoStoreState")


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

    @pydantic.root_validator(pre=True)
    def __unnest_progress(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        return {**values, **values.pop("progress")}


class ZZZEngagement(APIModel):
    """ZZZ engagement model."""

    current: int
    max: int


class ZZZNotes(APIModel):
    """Zenless Zone Zero sticky notes model."""

    battery_charge: BatteryCharge = Aliased("energy")
    engagement: ZZZEngagement = Aliased("vitality")
    scratch_card_completed: bool = Aliased("card_sign")
    video_store_state: VideoStoreState

    @pydantic.validator("scratch_card_completed", pre=True)
    def __transform_value(cls, v: typing.Literal["CardSignDone", "CardSignNotDone"]) -> bool:
        return v == "CardSignDone"

    @pydantic.root_validator(pre=True)
    def __unnest_value(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        values["video_store_state"] = values["vhs_sale"]["sale_state"]
        return values
