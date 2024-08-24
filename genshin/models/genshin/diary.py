"""Genshin diary models."""

import enum
import typing

import pydantic

from genshin.models.model import APIModel, UTC8Timestamp

__all__ = [
    "BaseDiary",
    "DayDiaryData",
    "Diary",
    "DiaryAction",
    "DiaryActionCategory",
    "DiaryPage",
    "DiaryType",
    "MonthDiaryData",
    "StarRailDayDiaryData",
    "StarRailDiary",
    "StarRailDiaryAction",
    "StarRailDiaryActionCategory",
    "StarRailDiaryPage",
    "StarRailDiaryType",
    "StarRailMonthDiaryData",
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
    server: str = pydantic.Field(alias="region")
    nickname: str = ""
    month: int = pydantic.Field(alias="data_month")


class DiaryActionCategory(APIModel):
    """Diary category for primogems."""

    id: int = pydantic.Field(alias="action_id")
    name: str = pydantic.Field(alias="action")
    amount: int = pydantic.Field(alias="num")
    percentage: int = pydantic.Field(alias="percent")


class MonthDiaryData(APIModel):
    """Diary data for a month."""

    current_primogems: int
    current_mora: int
    last_primogems: int
    last_mora: int
    primogems_rate: int = pydantic.Field(alias="primogem_rate")
    mora_rate: int
    categories: typing.Sequence[DiaryActionCategory] = pydantic.Field(alias="group_by")


class DayDiaryData(APIModel):
    """Diary data for a day."""

    current_primogems: int
    current_mora: int


class Diary(BaseDiary):
    """Traveler's diary."""

    data: MonthDiaryData = pydantic.Field(alias="month_data")
    day_data: DayDiaryData

    @property
    def month_data(self) -> MonthDiaryData:
        return self.data


class DiaryAction(APIModel):
    """Action which earned currency."""

    action_id: int
    action: str
    time: UTC8Timestamp
    amount: int = pydantic.Field(alias="num")


class DiaryPage(BaseDiary):
    """Page of a diary."""

    actions: typing.Sequence[DiaryAction] = pydantic.Field(alias="list")


class StarRailDiaryActionCategory(APIModel):
    """Diary category for rails_pass ."""

    id: str = pydantic.Field(alias="action")
    name: str = pydantic.Field(alias="action_name")
    amount: int = pydantic.Field(alias="num")
    percentage: int = pydantic.Field(alias="percent")


class StarRailMonthDiaryData(APIModel):
    """Diary data for a month."""

    current_hcoin: int
    current_rails_pass: int
    last_hcoin: int
    last_rails_pass: int
    hcoin_rate: int
    rails_rate: int
    categories: typing.Sequence[StarRailDiaryActionCategory] = pydantic.Field(alias="group_by")


class StarRailDayDiaryData(APIModel):
    """Diary data for a day."""

    current_hcoin: int
    current_rails_pass: int
    last_hcoin: int
    last_rails_pass: int


class StarRailDiary(BaseDiary):
    """Traveler's diary."""

    data: StarRailMonthDiaryData = pydantic.Field(alias="month_data")
    day_data: StarRailDayDiaryData

    @property
    def month_data(self) -> StarRailMonthDiaryData:
        return self.data


class StarRailDiaryType(enum.IntEnum):
    """Type of diary pages."""

    STELLARJADE = 1
    """STELLARJADE."""

    STARRAILPASS = 2
    """STARRAILPASS."""


class StarRailDiaryAction(APIModel):
    """Action which earned currency."""

    action: str
    action_name: str
    time: UTC8Timestamp
    amount: int = pydantic.Field(alias="num")


class StarRailDiaryPage(BaseDiary):
    """Page of a diary."""

    actions: typing.Sequence[StarRailDiaryAction] = pydantic.Field(alias="list")
