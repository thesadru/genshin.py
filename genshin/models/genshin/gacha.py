"""Genshin wish models."""

import datetime
import enum
import re
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, Unique

__all__ = [
    "BannerDetailItem",
    "BannerDetails",
    "BannerDetailsUpItem",
    "GachaItem",
    "GenshinBannerType",
    "SignalSearch",
    "StarRailBannerType",
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


class BaseWish(APIModel, Unique):
    """Base wish model."""

    uid: int
    id: int
    name: str
    rarity: int = Aliased("rank_type")

    tz_offset: int
    """Number of hours from UTC+8."""
    time: datetime.datetime
    """Timezone-aware time of when the wish was made"""

    @pydantic.field_validator("time", mode="before")
    def __parse_time(cls, v: str, info: pydantic.ValidationInfo) -> datetime.datetime:
        return datetime.datetime.fromisoformat(v).replace(
            tzinfo=datetime.timezone(datetime.timedelta(hours=8 + info.data["tz_offset"]))
        )


class Wish(BaseWish):
    """Wish made on any banner."""

    type: str = Aliased("item_type")
    banner_type: GenshinBannerType

    @pydantic.field_validator("banner_type", mode="before")
    def __cast_banner_type(cls, v: typing.Any) -> int:
        return int(v)


class Warp(BaseWish):
    """Warp made on any banner."""

    item_id: int
    type: str = Aliased("item_type")

    banner_type: StarRailBannerType
    banner_id: int = Aliased("gacha_id")

    @pydantic.field_validator("banner_type", mode="before")
    def __cast_banner_type(cls, v: typing.Any) -> int:
        return int(v)


class SignalSearch(BaseWish):
    """Signal Search made on any banner."""

    item_id: int
    type: str = Aliased("item_type")

    banner_type: ZZZBannerType

    @pydantic.field_validator("banner_type", mode="before")
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

    @pydantic.field_validator("element", mode="before")
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

    r5_items: list[BannerDetailItem] = Aliased("r5_prob_list")
    r4_items: list[BannerDetailItem] = Aliased("r4_prob_list")
    r3_items: list[BannerDetailItem] = Aliased("r3_prob_list")

    @pydantic.field_validator("r5_up_items", "r4_up_items", mode="before")
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


class GachaItem(APIModel, Unique):
    """Item that can be gotten from the gacha."""

    name: str
    type: str = Aliased("item_type")
    rarity: int = Aliased("rank_type")
    id: int = Aliased("item_id")

    @pydantic.field_validator("id")
    def __format_id(cls, v: int) -> int:
        return 10000000 + v - 1000 if len(str(v)) == 4 else v

    def is_character(self) -> bool:
        """Whether this item is a character."""
        return len(str(self.id)) == 8
