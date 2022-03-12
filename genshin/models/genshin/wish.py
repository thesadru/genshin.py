"""Genshin wish models."""
import datetime
import re
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, Unique

__all__ = [
    "BANNER_TYPES",
    "BannerDetailItem",
    "BannerDetails",
    "BannerDetailsUpItem",
    "BannerType",
    "GachaItem",
    "Wish",
]

BannerType = typing.Literal[100, 200, 301, 302, 400]

BANNER_TYPES: typing.Sequence[BannerType] = [100, 200, 301, 302, 400]


class Wish(APIModel, Unique):
    """Wish made on any banner."""

    uid: int

    id: int
    type: str = Aliased("item_type")
    name: str
    rarity: int = Aliased("rank_type")
    time: datetime.datetime

    banner_type: BannerType = Aliased("gacha_type")
    banner_name: str

    @pydantic.validator("banner_type", pre=True)
    def __cast_banner_type(cls, v: typing.Any) -> int:
        return int(v)


class BannerDetailItem(APIModel):
    """Item that may be gotten from a banner."""

    name: str = Aliased("item_name")
    type: str = Aliased("item_type")
    rarity: int = Aliased("rank")

    up: bool = Aliased("is_up")
    order: int = Aliased("order_value")


class BannerDetailsUpItem(APIModel):
    """Item that has a rate-up on a banner."""

    name: str = Aliased("item_name")
    type: str = Aliased("item_type")
    element: str = Aliased("item_attr")
    icon: str = Aliased("item_img")

    @pydantic.validator("element", pre=True)
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
    banner_type: int = Aliased("gacha_type")
    title: str
    content: str
    date_range: str

    r5_up_prob: typing.Optional[float]
    r4_up_prob: typing.Optional[float]
    r5_prob: typing.Optional[float]
    r4_prob: typing.Optional[float]
    r3_prob: typing.Optional[float]
    r5_guarantee_prob: typing.Optional[float] = Aliased("r5_baodi_prob")
    r4_guarantee_prob: typing.Optional[float] = Aliased("r4_baodi_prob")
    r3_guarantee_prob: typing.Optional[float] = Aliased("r3_baodi_prob")

    r5_up_items: typing.Sequence[BannerDetailsUpItem]
    r4_up_items: typing.Sequence[BannerDetailsUpItem]

    r5_items: typing.List[BannerDetailItem] = Aliased("r5_prob_list")
    r4_items: typing.List[BannerDetailItem] = Aliased("r4_prob_list")
    r3_items: typing.List[BannerDetailItem] = Aliased("r3_prob_list")

    @pydantic.validator("r5_up_items", "r4_up_items", pre=True)
    def __replace_none(cls, v: typing.Optional[typing.Sequence[typing.Any]]) -> typing.Sequence[typing.Any]:
        return v or []

    @pydantic.validator(
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
    def __parse_percentage(cls, v: str) -> typing.Optional[float]:
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


class GachaItem(APIModel, Unique):
    """Item that can be gotten from the gacha."""

    name: str
    type: str = Aliased("item_type")
    rarity: int = Aliased("rank_type")
    id: int = Aliased("item_id")

    @pydantic.validator("id")
    def __format_id(cls, v: int) -> int:
        return 10000000 + v - 1000 if len(str(v)) == 4 else v

    def is_character(self) -> bool:
        """Whether this item is a character."""
        return len(str(self.id)) == 8
