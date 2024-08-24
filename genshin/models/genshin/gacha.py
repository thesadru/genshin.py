"""Genshin wish models."""

import datetime
import enum
import re
import typing

import pydantic

from genshin.models.model import APIModel

__all__ = [
    "BannerDetailItem",
    "BannerDetails",
    "BannerDetailsUpItem",
    "GachaItem",
    "GenshinBannerType",
    "SignalSearch",
    "Warp",
    "Wish",
    "ZZZBannerType",
]


class GenshinBannerType(enum.IntEnum):
    """Banner types in wish histories."""

    NOVICE = 100
    """Temporary novice banner."""

    STANDARD = PERMANENT = 200
    """Permanent standard banner."""

    CHARACTER = 301
    """Rotating character banner."""

    WEAPON = 302
    """Rotating weapon banner."""

    CHRONICLED = 500
    """Chronicled banner."""

    # these are special cases
    # they exist inside the history but should be counted as the same

    CHARACTER1 = 301
    """Character banner #1."""

    CHARACTER2 = 400
    """Character banner #2."""


class StarRailBannerType(enum.IntEnum):
    """Banner types in wish histories."""

    STANDARD = PERMANENT = 1
    """Permanent standard banner."""
    NOVICE = 2
    """Temporary novice banner."""
    CHARACTER = 11
    """Rotating character banner."""
    WEAPON = 12
    """Rotating weapon banner."""


class ZZZBannerType(enum.IntEnum):
    """Banner types in wish histories."""

    STANDARD = PERMANENT = 1
    """Permanent standard banner."""

    CHARACTER = 2
    """Rotating character banner."""

    WEAPON = 3
    """Rotating weapon banner."""

    BANGBOO = 5
    """Bangboo banner."""


class Wish(APIModel):
    """Wish made on any banner."""

    uid: int

    id: int
    type: str = pydantic.Field(alias="item_type")
    name: str
    rarity: int = pydantic.Field(alias="rank_type")
    time: datetime.datetime

    banner_type: GenshinBannerType

    @pydantic.field_validator("banner_type", mode="before")
    @classmethod
    def __cast_banner_type(cls, v: typing.Any) -> int:
        return int(v)


class Warp(APIModel):
    """Warp made on any banner."""

    uid: int

    id: int
    item_id: int
    type: str = pydantic.Field(alias="item_type")
    name: str
    rarity: int = pydantic.Field(alias="rank_type")
    time: datetime.datetime

    banner_type: StarRailBannerType
    banner_id: int = pydantic.Field(alias="gacha_id")

    @pydantic.field_validator("banner_type", mode="before")
    @classmethod
    def __cast_banner_type(cls, v: typing.Any) -> int:
        return int(v)


class SignalSearch(APIModel):
    """Signal Search made on any banner."""

    uid: int

    id: int
    item_id: int
    type: str = pydantic.Field(alias="item_type")
    name: str
    rarity: int = pydantic.Field(alias="rank_type")
    time: datetime.datetime

    banner_type: ZZZBannerType

    @pydantic.field_validator("banner_type", mode="before")
    @classmethod
    def __cast_banner_type(cls, v: typing.Any) -> int:
        return int(v)


class BannerDetailItem(APIModel):
    """Item that may be gotten from a banner."""

    name: str = pydantic.Field(alias="item_name")
    type: str = pydantic.Field(alias="item_type")
    rarity: int = pydantic.Field(alias="rank")

    up: bool = pydantic.Field(alias="is_up")
    order: int = pydantic.Field(alias="order_value")


class BannerDetailsUpItem(APIModel):
    """Item that has a rate-up on a banner."""

    name: str = pydantic.Field(alias="item_name")
    type: str = pydantic.Field(alias="item_type")
    element: str = pydantic.Field(alias="item_attr")
    icon: str = pydantic.Field(alias="item_img")

    @pydantic.field_validator("element", mode="before")
    @classmethod
    def __parse_element(cls, v: str) -> str:
        return {
            "风": "Anemo",
            "火": "Pyro",
            "水": "Hydro",
            "雷": "Electro",
            "冰": "Cryo",
            "岩": "Geo",
            "草": "Dendro",
            "": "",
        }.get(v, v)


class BannerDetails(APIModel):
    """Details of a banner."""

    banner_id: str
    banner_type: int = pydantic.Field(alias="gacha_type")
    title: str
    content: str
    date_range: str

    r5_up_prob: typing.Optional[float]
    r4_up_prob: typing.Optional[float]
    r5_prob: typing.Optional[float]
    r4_prob: typing.Optional[float]
    r3_prob: typing.Optional[float]
    r5_guarantee_prob: typing.Optional[float] = pydantic.Field(alias="r5_baodi_prob")
    r4_guarantee_prob: typing.Optional[float] = pydantic.Field(alias="r4_baodi_prob")
    r3_guarantee_prob: typing.Optional[float] = pydantic.Field(alias="r3_baodi_prob")

    r5_up_items: typing.Sequence[BannerDetailsUpItem]
    r4_up_items: typing.Sequence[BannerDetailsUpItem]

    r5_items: typing.List[BannerDetailItem] = pydantic.Field(alias="r5_prob_list")
    r4_items: typing.List[BannerDetailItem] = pydantic.Field(alias="r4_prob_list")
    r3_items: typing.List[BannerDetailItem] = pydantic.Field(alias="r3_prob_list")

    @pydantic.field_validator("r5_up_items", "r4_up_items", mode="before")
    @classmethod
    def __replace_none(cls, v: typing.Optional[typing.Sequence[typing.Any]]) -> typing.Sequence[typing.Any]:
        return v or []

    @pydantic.field_validator(
        "r5_up_prob",
        "r4_up_prob",
        "r5_prob",
        "r4_prob",
        "r3_prob",
        "r5_guarantee_prob",
        "r4_guarantee_prob",
        "r3_guarantee_prob",
        mode="before",
    )
    def __parse_percentage(cls, v: typing.Optional[str]) -> typing.Optional[float]:
        if v is None or isinstance(v, (int, float)):
            return v

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
            400: "Character Event Wish",
        }
        return banners[self.banner_type]

    @property
    def items(self) -> typing.Sequence[BannerDetailItem]:
        items = self.r5_items + self.r4_items + self.r3_items
        return sorted(items, key=lambda x: x.order)


class GachaItem(APIModel):
    """Item that can be gotten from the gacha."""

    name: str
    type: str = pydantic.Field(alias="item_type")
    rarity: int = pydantic.Field(alias="rank_type")
    id: int = pydantic.Field(alias="item_id")

    @pydantic.field_validator("id")
    @classmethod
    def __format_id(cls, v: int) -> int:
        return 10000000 + v - 1000 if len(str(v)) == 4 else v

    def is_character(self) -> bool:
        """Whether this item is a character."""
        return len(str(self.id)) == 8
