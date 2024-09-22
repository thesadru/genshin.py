"""Starrail Rogue models."""

from genshin.models.model import APIModel

from ..character import RogueCharacter
from .base import PartialTime


class RogueUserRole(APIModel):
    """Rogue User info."""

    nickname: str
    server: str
    level: int


class RogueBasicInfo(APIModel):
    """generalized rogue basic info."""

    unlocked_buff_num: int
    unlocked_miracle_num: int
    unlocked_skill_points: int


class RogueRecordBasic(APIModel):
    """Basic record info."""

    id: int
    finish_cnt: int
    schedule_begin: PartialTime
    schedule_end: PartialTime


class RogueBuffType(APIModel):
    """Rogue buff type."""

    id: int
    name: str
    cnt: int


class RogueBuffItem(APIModel):
    """Rogue buff item."""

    id: int
    name: str
    is_evoluted: bool
    rank: int


class RogueBuff(APIModel):
    """Rogue buff info."""

    base_type: RogueBuffType
    items: list[RogueBuffItem]


class RogueMiracle(APIModel):
    """Rogue miracle info."""

    id: int
    name: str
    icon: str


class RogueRecordDetail(APIModel):
    """Detailed record info."""

    name: str
    finish_time: PartialTime
    score: int
    final_lineup: list[RogueCharacter]
    base_type_list: list[RogueBuffType]
    cached_avatars: list[RogueCharacter]
    buffs: list[RogueBuff]
    miracles: list[RogueMiracle]
    difficulty: int
    progress: int


class RogueRecord(APIModel):
    """generic record data."""

    basic: RogueRecordBasic
    records: list[RogueRecordDetail]
    has_data: bool


class StarRailRogue(APIModel):
    """generic rogue data."""

    role: RogueUserRole
    basic_info: RogueBasicInfo
    current_record: RogueRecord
    last_record: RogueRecord
