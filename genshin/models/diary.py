from datetime import datetime
from typing import List

from pydantic import Field

from .base import GenshinModel


class BaseDiary(GenshinModel):
    uid: int
    region: str
    hoyolab_uid: int = Field(galias="account_id")
    nickname: str
    month: int
    data_month: int


class DiaryData(GenshinModel):
    current_primogems: int
    current_mora: int
    last_primogems: int
    last_mora: int


class DiaryGroupBy(GenshinModel):
    action_id: int
    action: str
    amount: int = Field(galias="num")
    percentage: int = Field(galias="percent")


class DiaryMonthData(GenshinModel):
    current_primogems_level: int  # ???
    primogems_rate: int
    mora_rate: int
    group_by: List[DiaryGroupBy]


class Diary(BaseDiary):
    day_data: DiaryData
    month_data: DiaryMonthData
    lantern: bool = False  # ???


class DiaryEntry(GenshinModel):
    action_id: int
    action: str
    time: datetime = Field(timezone=8)
    amount: int = Field(galias="num")


class DiaryPage(BaseDiary):
    page: int

    pages: List[DiaryEntry] = Field(galias="list")
