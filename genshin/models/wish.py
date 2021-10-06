import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class BannerType(int, Enum):
    novice = 100
    permanent = 200
    character = 301
    weapon = 302


class Wish(BaseModel):
    uid: int

    id: int
    type: str = Field(alias="item_type")
    name: str
    rarity: int = Field(alias="rank_type")
    time: datetime

    banner_type: BannerType = Field(alias="gacha_type")
    banner_name: str

    @validator("banner_type", pre=True)
    def __cast_banner_type(cls, v):
        return int(v)


class BannerDetailProb(BaseModel):
    name: str = Field(alias="item_name")
    type: str = Field(alias="item_type")
    rarity: int = Field(alias="rank")

    up: bool = Field(alias="is_up")
    order: int = Field(alias="order_value")


class BannerDetailsItem(BaseModel):
    name: str = Field(alias="item_name")
    type: str = Field(alias="item_type")
    element: str = Field(alias="item_attr")
    icon: str = Field(alias="item_img")

    @validator("element", pre=True)
    def __parse_element(cls, v):
        return {
            "风": "Anemo",
            "火": "Pyro",
            "水": "Hydro",
            "雷": "Electro",
            "冰": "Cryo",
            "岩": "Geo",
            "？": "Dendro",
            "": "",
        }[v]


class BannerDetails(BaseModel):
    banner_type: int = Field(alias="gacha_type")
    title: str
    content: str
    date_range: str

    r5_up_prob: Optional[float] = Field(alias="r5_up_prob")
    r4_up_prob: Optional[float] = Field(alias="r4_up_prob")
    r5_prob: Optional[float] = Field(alias="r5_prob")
    r4_prob: Optional[float] = Field(alias="r4_prob")
    r3_prob: Optional[float] = Field(alias="r3_prob")
    r5_guarantee_prob: Optional[float] = Field(alias="r5_baodi_prob")
    r4_guarantee_prob: Optional[float] = Field(alias="r4_baodi_prob")
    r3_guarantee_prob: Optional[float] = Field(alias="r3_baodi_prob")

    r5_up_items: List[BannerDetailsItem]
    r4_up_items: List[BannerDetailsItem]

    r5_items: List[BannerDetailProb] = Field(alias="r5_prob_list")
    r4_items: List[BannerDetailProb] = Field(alias="r4_prob_list")
    r3_items: List[BannerDetailProb] = Field(alias="r3_prob_list")

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
    def banner(self) -> str:
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
    def items(self):
        items = self.r5_items + self.r4_items + self.r3_items
        return sorted(items, key=lambda x: x.order)
