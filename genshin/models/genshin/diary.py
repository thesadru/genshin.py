"""Genshin diary models."""
import datetime
import enum
import typing

from genshin.models.model import Aliased, APIModel

__all__ = [
    "BaseDiary",
    "DayDiaryData",
    "Diary",
    "DiaryAction",
    "DiaryActionCategory",
    "DiaryPage",
    "DiaryType",
    "MonthDiaryData",
]


class DiaryType(enum.IntEnum):
    """Type of diary pages."""

    PRIMOGEMS = 1
    """Primogems."""

    MORA = 2
    """Mora."""


class BaseDiary(APIModel):
    """Base model for diary and diary page."""

    uid: int
    region: str
    nickname: str
    month: int = Aliased("data_month")


class DiaryActionCategory(APIModel):
    """Diary category for primogems."""

    id: int = Aliased("action_id")
    name: str = Aliased("action")
    amount: int = Aliased("num")
    percentage: int = Aliased("percent")


class MonthDiaryData(APIModel):
    """Diary data for a month."""

    current_primogems: int
    current_mora: int
    last_primogems: int
    last_mora: int
    primogems_rate: int = Aliased("primogem_rate")
    mora_rate: int
    categories: typing.Sequence[DiaryActionCategory] = Aliased("group_by")


class DayDiaryData(APIModel):
    """Diary data for a day."""

    current_primogems: int
    current_mora: int


class Diary(BaseDiary):
    """Traveler's diary."""

    data: MonthDiaryData = Aliased("month_data")
    day_data: DayDiaryData


class DiaryAction(APIModel):
    """Action which earned currency."""

    action_id: int
    action: str
    time: datetime.datetime = Aliased(timezone=8)
    amount: int = Aliased("num")


class DiaryPage(BaseDiary):
    """Page of a diary."""

    actions: typing.Sequence[DiaryAction] = Aliased("list")
