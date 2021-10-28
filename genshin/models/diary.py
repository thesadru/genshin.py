from datetime import datetime
from typing import List

from pydantic import Field

from .base import GenshinModel


class BaseDiary(GenshinModel):
    """Base model for diary and diary page"""

    uid: int
    region: str
    nickname: str
    month: int = Field(galias="data_month")


class DiaryGroupBy(GenshinModel):
    """A diary earn category"""

    action_id: int
    action: str
    amount: int = Field(galias="num")
    percentage: int = Field(galias="percent")


class DiaryData(GenshinModel):
    """Diary data for a month"""

    current_primogems: int
    current_mora: int
    primogems_rate: int = 0
    mora_rate: int = 0
    group_by: List[DiaryGroupBy]


class Diary(BaseDiary):
    """A traveler's diary"""

    data: DiaryData = Field(galias="month_data")


class DiaryAction(GenshinModel):
    """An action which earned currency"""

    action_id: int
    action: str
    time: datetime = Field(timezone=8)
    amount: int = Field(galias="num")


class DiaryPage(BaseDiary):
    """A page of a diary"""

    actions: List[DiaryAction] = Field(galias="list")
