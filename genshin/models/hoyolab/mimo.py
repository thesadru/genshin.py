import typing

import pydantic
from genshin.models.model import APIModel, Aliased
import enum

__all__ = ("MimoTask", "MimoTaskStatus")


class MimoTaskStatus(enum.IntEnum):
    """Mimo task status."""

    FINISHED = 1
    ONGOING = 2
    CLAIMED = 3


class MimoTaskType(enum.IntEnum):
    """Mimo task type."""

    FINISHABLE = 1
    COMMUNITY = 3
    DAILY_LOGIN = 12
    CONSECUTIVE_LOGIN = 13
    IN_GAME = 16


class MimoTask(APIModel):
    """Mimo task."""

    id: int = Aliased("task_id")
    name: str = Aliased("task_name")
    time_type: int
    point: int
    progress: int
    total_progress: int

    status: MimoTaskStatus
    jump_url: str
    window_text: str
    type: typing.Union[int, MimoTaskType] = Aliased("task_type")
    af_url: str

    @pydantic.field_validator("type", mode="before")
    def __transform_task_type(cls, v: int) -> typing.Union[int, MimoTaskType]:
        try:
            return MimoTaskType(v)
        except ValueError:
            return v


class MimoShopItem(APIModel):
    """Mimo shop item."""

    id: int = Aliased("award_id")
    status: int
    icon: str
    name: str
    cost: int
    stock: int
