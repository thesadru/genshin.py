"""Genshin chronicle notes."""

import datetime
import enum
import typing

import pydantic

from genshin.models.model import APIModel

__all__ = [
    "ArchonQuest",
    "ArchonQuestProgress",
    "ArchonQuestStatus",
    "AttendanceReward",
    "AttendanceRewardStatus",
    "DailyTasks",
    "Expedition",
    "Notes",
    "TaskReward",
    "TaskRewardStatus",
]


def _process_timedelta(time: typing.Union[int, datetime.timedelta, datetime.datetime]) -> datetime.datetime:
    if isinstance(time, int):
        time = datetime.datetime.fromtimestamp(time).astimezone()

    if isinstance(time, datetime.timedelta):
        time = datetime.datetime.now().astimezone() + time

    if time < datetime.datetime(2000, 1, 1).astimezone():
        delta = datetime.timedelta(seconds=int(time.timestamp()))
        time = datetime.datetime.now().astimezone() + delta

    time = time.replace(second=0, microsecond=0)

    return time


class Expedition(APIModel):
    """Real-Time note expedition."""

    character_icon: str = pydantic.Field(alias="avatar_side_icon")
    status: typing.Literal["Ongoing", "Finished"]
    remaining_time: datetime.timedelta = pydantic.Field(alias="remained_time")

    @property
    def finished(self) -> bool:
        """Whether the expedition has finished."""
        return self.remaining_time <= datetime.timedelta(0)

    @property
    def completion_time(self) -> datetime.datetime:
        return datetime.datetime.now().astimezone() + self.remaining_time


class TransformerTimedelta(datetime.timedelta):
    """Transformer recovery time."""

    @property
    def timedata(self) -> typing.Tuple[int, int, int, int]:
        seconds: int = super().seconds
        days: int = super().days
        hour, second = divmod(seconds, 3600)
        minute, second = divmod(second, 60)

        return days, hour, minute, second

    @property
    def hours(self) -> int:
        return self.timedata[1]

    @property
    def minutes(self) -> int:
        return self.timedata[2]

    @property
    def seconds(self) -> int:
        return self.timedata[3]


class TaskRewardStatus(str, enum.Enum):
    """Task Reward Statuses."""

    UNFINISHED = "TaskRewardStatusUnfinished"
    FINISHED = "TaskRewardStatusFinished"
    COLLECTED = "TaskRewardStatusTakenAward"


class TaskReward(APIModel):
    """Status of the Commission/Task."""

    status: typing.Union[TaskRewardStatus, str]

    @pydantic.field_validator("status", mode="before")
    @classmethod
    def __prevent_enum_crash(cls, v: str) -> typing.Union[TaskRewardStatus, str]:
        try:
            return TaskRewardStatus(v)
        except ValueError:
            return v


class AttendanceRewardStatus(str, enum.Enum):
    """Attendance Reward Statuses."""

    AVAILABLE = "AttendanceRewardStatusWaitTaken"
    COLLECTED = "AttendanceRewardStatusTakenAward"
    FORBIDDEN = "AttendanceRewardStatusForbid"
    UNAVAILABLE = "AttendanceRewardStatusUnfinished"


class AttendanceReward(APIModel):
    """Status of the Encounter Point."""

    status: typing.Union[AttendanceRewardStatus, str]
    progress: int

    @pydantic.field_validator("status", mode="before")
    @classmethod
    def __prevent_enum_crash(cls, v: str) -> typing.Union[AttendanceRewardStatus, str]:
        try:
            return AttendanceRewardStatus(v)
        except ValueError:
            return v


class DailyTasks(APIModel):
    """Daily tasks section."""

    max_tasks: int = pydantic.Field(alias="total_num")
    completed_tasks: int = pydantic.Field(alias="finished_num")
    claimed_commission_reward: bool = pydantic.Field(alias="is_extra_task_reward_received")

    task_rewards: typing.Sequence[TaskReward]
    attendance_rewards: typing.Sequence[AttendanceReward]
    attendance_visible: bool

    stored_attendance: float
    stored_attendance_refresh_countdown: datetime.timedelta = pydantic.Field(alias="attendance_refresh_time")


class ArchonQuestStatus(str, enum.Enum):
    """Archon quest status."""

    ONGOING = "StatusOngoing"
    NOT_OPEN = "StatusNotOpen"


class ArchonQuest(APIModel):
    """Archon Quest."""

    id: int
    status: ArchonQuestStatus
    chapter_num: str
    chapter_title: str


class ArchonQuestProgress(APIModel):
    """Archon Quest Progress."""

    list: typing.Sequence[ArchonQuest]
    mainlines_finished: bool = pydantic.Field(alias="is_finish_all_mainline")
    archon_quest_unlocked: bool = pydantic.Field(alias="is_open_archon_quest")
    interchapters_finished: bool = pydantic.Field(alias="is_finish_all_interchapter")


class Notes(APIModel):
    """Real-Time notes."""

    current_resin: int
    max_resin: int
    remaining_resin_recovery_time: datetime.timedelta = pydantic.Field(alias="resin_recovery_time")

    current_realm_currency: int = pydantic.Field(alias="current_home_coin")
    max_realm_currency: int = pydantic.Field(alias="max_home_coin")
    remaining_realm_currency_recovery_time: datetime.timedelta = pydantic.Field(alias="home_coin_recovery_time")

    completed_commissions: int = pydantic.Field(alias="finished_task_num")
    max_commissions: int = pydantic.Field(alias="total_task_num")
    claimed_commission_reward: bool = pydantic.Field(alias="is_extra_task_reward_received")

    remaining_resin_discounts: int = pydantic.Field(alias="remain_resin_discount_num")
    max_resin_discounts: int = pydantic.Field(alias="resin_discount_num_limit")

    remaining_transformer_recovery_time: typing.Optional[TransformerTimedelta]

    expeditions: typing.Sequence[Expedition]
    max_expeditions: int = pydantic.Field(alias="max_expedition_num")

    archon_quest_progress: ArchonQuestProgress

    @property
    def resin_recovery_time(self) -> datetime.datetime:
        """The time when resin will be recovered."""
        return datetime.datetime.now().astimezone() + self.remaining_resin_recovery_time

    @property
    def realm_currency_recovery_time(self) -> datetime.datetime:
        """The time when realm currency will be recovered."""
        return datetime.datetime.now().astimezone() + self.remaining_realm_currency_recovery_time

    @property
    def transformer_recovery_time(self) -> typing.Optional[datetime.datetime]:
        """The time the transformer will be recovered."""
        if self.remaining_transformer_recovery_time is None:
            return None

        remaining = datetime.datetime.now().astimezone() + self.remaining_transformer_recovery_time
        return remaining

    @pydantic.model_validator(mode="before")
    @classmethod
    def __flatten_transformer(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        if "transformer_recovery_time" in values:
            return values

        if values.get("transformer") and values["transformer"]["obtained"]:
            t = values["transformer"]["recovery_time"]
            delta = TransformerTimedelta(days=t["Day"], hours=t["Hour"], minutes=t["Minute"], seconds=t["Second"])
            values["remaining_transformer_recovery_time"] = delta
        else:
            values["remaining_transformer_recovery_time"] = None

        return values

    daily_task: DailyTasks
