import re
from datetime import datetime
from enum import IntEnum
from typing import List, Literal, Optional

from pydantic import Field, validator

from .base import GenshinModel

BannerType = Literal[100, 200, 301, 302]


class Wish(GenshinModel):
    """A wish made on any banner"""

    uid: int

    id: int
    type: str = Field(galias="item_type")
    name: str
    rarity: int = Field(galias="rank_type")
    time: datetime

    banner_type: BannerType = Field(galias="gacha_type")
    banner_name: str

    @validator("banner_type", pre=True)
    def __cast_banner_type(cls, v):
        return int(v)


class BannerDetailItem(GenshinModel):
    """An item that may be gotten from a banner"""

    name: str = Field(galias="item_name")
    type: str = Field(galias="item_type")
    rarity: int = Field(galias="rank")

    up: bool = Field(galias="is_up")
    order: int = Field(galias="order_value")


class BannerDetailsUpItem(GenshinModel):
    """An item that has a rate-up on a banner"""

    name: str = Field(galias="item_name")
    type: str = Field(galias="item_type")
    element: str = Field(galias="item_attr")
    icon: str = Field(galias="item_img")

    @validator("element", pre=True)
    def __parse_element(cls, v):
        return {
            "风": "Anemo",
            "火": "Pyro",
            "水": "Hydro",
            "雷": "Electro",
            "冰": "Cryo",
            "岩": "Geo",
            "草": "Dendro",
            "": "",
        }[v]


class BannerDetails(GenshinModel):
    """Details of a banner"""

    banner_type: int = Field(galias="gacha_type")
    title: str
    content: str
    date_range: str

    r5_up_prob: Optional[float]
    r4_up_prob: Optional[float]
    r5_prob: Optional[float]
    r4_prob: Optional[float]
    r3_prob: Optional[float]
    r5_guarantee_prob: Optional[float] = Field(galias="r5_baodi_prob")
    r4_guarantee_prob: Optional[float] = Field(galias="r4_baodi_prob")
    r3_guarantee_prob: Optional[float] = Field(galias="r3_baodi_prob")

    r5_up_items: List[BannerDetailsUpItem]
    r4_up_items: List[BannerDetailsUpItem]

    r5_items: List[BannerDetailItem] = Field(galias="r5_prob_list")
    r4_items: List[BannerDetailItem] = Field(galias="r4_prob_list")
    r3_items: List[BannerDetailItem] = Field(galias="r3_prob_list")

    @validator("r5_up_items", "r4_up_items", pre=True)
    def __replace_none(cls, v):
        return v or []

    @validator(
        "r5_up_prob",
        "r4_up_prob",
        "r5_prob",
        "r4_prob",
        "r3_prob",
        "r5_guarantee_prob",
        "r4_guarantee_prob",
        "r3_guarantee_prob",
        pre=True,
    )
    def __parse_percentage(cls, v):
        return None if v == "0%" else float(v[:-1].replace(",", "."))

    @property
    def name(self) -> str:
        return re.sub(r"<.*?>", "", self.title).strip()

    @property
    def banner_type_name(self) -> str:
        banners = {
            100: "Novice Wishes",
            200: "Permanent Wish",
            301: "Character Event Wish",
            302: "Weapon Event Wish",
        }
        return banners[self.banner_type]

    @property
    def items(self) -> List[BannerDetailItem]:
        items = self.r5_items + self.r4_items + self.r3_items
        return sorted(items, key=lambda x: x.order)


class GachaItem(GenshinModel):
    """An item that can be gotten from the gacha"""

    name: str
    type: str = Field(galias="item_type")
    rarity: int = Field(galias="rank_type")
    id: int = Field(galias="item_id")

    @validator("id")
    def __format_id(cls, v):
        return 10000000 + v - 1000 if len(str(v)) == 4 else v

    def is_character(self) -> bool:
        return len(str(self.id)) == 8
