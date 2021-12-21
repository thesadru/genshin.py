from datetime import datetime
from typing import List

from pydantic import Field

from genshin import models

__all__ = [
    "BaseDiary",
    "DiaryActionCategory",
    "DiaryData",
    "DayDiaryData",
    "Diary",
    "DiaryAction",
    "DiaryPage",
]


class BaseDiary(models.APIModel):
    """Base model for diary and diary page"""

    uid: int
    region: str
    nickname: str
    month: int = Field(galias="data_month")


class DiaryActionCategory(models.APIModel):
    """A diary category for primogems"""

    id: int = Field(galias="action_id")
    name: str = Field(galias="action")
    amount: int = Field(galias="num")
    percentage: int = Field(galias="percent")


class DiaryData(models.APIModel):
    """Diary data for a month"""

    current_primogems: int
    current_mora: int
    last_primogems: int
    last_mora: int
    primogems_rate: int = Field(galias="primogem_rate")
    mora_rate: int
    categories: List[DiaryActionCategory] = Field(galias="group_by")


class DayDiaryData(models.APIModel):
    """Diary data for a day"""

    current_primogems: int
    current_mora: int


class Diary(BaseDiary):
    """A traveler's diary"""

    data: DiaryData = Field(galias="month_data")
    day_data: DayDiaryData


class DiaryAction(models.APIModel):
    """An action which earned currency"""

    action_id: int
    action: str
    time: datetime = Field(timezone=8)
    amount: int = Field(galias="num")


class DiaryPage(BaseDiary):
    """A page of a diary"""

    actions: List[DiaryAction] = Field(galias="list")
