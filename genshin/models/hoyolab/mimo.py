import datetime
import enum
import typing

import pydantic

from genshin import types
from genshin.models.model import Aliased, APIModel, DateTimeField

__all__ = ("MimoGame", "MimoShopItem", "MimoShopItemStatus", "MimoTask", "MimoTaskStatus", "MimoTaskType")


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


class MimoShopItemStatus(enum.IntEnum):
    """Mimo shop item status."""

    EXCHANGEABLE = 1
    NOT_EXCHANGEABLE = 2
    LIMIT_REACHED = 3
    SOLD_OUT = 4


class MimoGame(APIModel):
    """Mimo game."""

    id: int = Aliased("game_id")
    version_id: int
    expire_point: bool
    point: int
    start_time: DateTimeField
    end_time: DateTimeField

    @property
    def game(self) -> typing.Union[typing.Literal["hoyolab"], types.Game, int]:
        if self.id == 5:
            return "hoyolab"
        if self.id == 6:
            return types.Game.STARRAIL
        if self.id == 8:
            return types.Game.ZZZ
        return self.id


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
    status: MimoShopItemStatus
    icon: str
    name: str
    cost: int
    stock: int
    user_count: int
    next_refresh_time: datetime.timedelta
    expire_day: int
