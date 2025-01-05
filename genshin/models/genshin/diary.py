"""Genshin diary models."""

import enum
import typing

from genshin.models.model import Aliased, APIModel, TZDateTime

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
    server: str = Aliased("region")
    nickname: str = ""
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

    @property
    def month_data(self) -> MonthDiaryData:
        return self.data


class DiaryAction(APIModel):
    """Action which earned currency."""

    action_id: int
    action: str
    time: TZDateTime
    amount: int = Aliased("num")


class DiaryPage(BaseDiary):
    """Page of a diary."""

    actions: typing.Sequence[DiaryAction] = Aliased("list")


class StarRailDiaryActionCategory(APIModel):
    """Diary category for rails_pass ."""

    id: str = Aliased("action")
    name: str = Aliased("action_name")
    amount: int = Aliased("num")
    percentage: int = Aliased("percent")


class StarRailMonthDiaryData(APIModel):
    """Diary data for a month."""

    current_hcoin: int
    current_rails_pass: int
    last_hcoin: int
    last_rails_pass: int
    hcoin_rate: int
    rails_rate: int
    categories: typing.Sequence[StarRailDiaryActionCategory] = Aliased("group_by")


class StarRailDayDiaryData(APIModel):
    """Diary data for a day."""

    current_hcoin: int
    current_rails_pass: int
    last_hcoin: int
    last_rails_pass: int


class StarRailDiary(BaseDiary):
    """Traveler's diary."""

    data: StarRailMonthDiaryData = Aliased("month_data")
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
    time: TZDateTime
    amount: int = Aliased("num")


class StarRailDiaryPage(BaseDiary):
    """Page of a diary."""

    actions: typing.Sequence[StarRailDiaryAction] = Aliased("list")
