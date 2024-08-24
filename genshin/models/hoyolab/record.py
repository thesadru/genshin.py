"""Base hoyolab APIModels."""

from __future__ import annotations

import enum
import re
import typing

import pydantic

from genshin import types
from genshin.models.model import APIModel

__all__ = [
    "FullHoyolabUser",
    "Gender",
    "GenshinAccount",
    "HoyolabUserCertification",
    "HoyolabUserLevel",
    "PartialHoyolabUser",
    "RecordCard",
    "RecordCardData",
    "RecordCardSetting",
    "RecordCardSettingType",
    "UserInfo",
]


class GenshinAccount(APIModel):
    """Genshin account."""

    game_biz: str
    uid: int = pydantic.Field(alias="game_uid")
    level: int
    nickname: str
    server: str = pydantic.Field(alias="region")
    server_name: str = pydantic.Field(alias="region_name")

    @property
    def game(self) -> types.Game:
        if "hk4e" in self.game_biz:
            return types.Game.GENSHIN
        if "bh3" in self.game_biz:
            return types.Game.HONKAI
        if "hkrpg" in self.game_biz:
            return types.Game.STARRAIL
        if "nap" in self.game_biz:
            return types.Game.ZZZ
        if "nxx" in self.game_biz:
            return types.Game.TOT

        try:
            return types.Game(self.game_biz)
        except ValueError:
            return self.game_biz  # type: ignore


class UserInfo(APIModel):
    """Chronicle user info."""

    nickname: str
    server: str = pydantic.Field(alias="region")
    level: int
    icon: str = pydantic.Field(alias="AvatarUrl")


class RecordCardData(APIModel):
    """Data entry of a record card."""

    name: str
    value: str


class RecordCardSetting(APIModel):
    """Privacy setting of a record card."""

    id: int = pydantic.Field(alias="switch_id")
    description: str = pydantic.Field(alias="switch_name")
    public: bool = pydantic.Field(alias="is_public")


class RecordCardSettingType(enum.IntEnum):
    """Privacy setting of a record card."""

    SHOW_CHRONICLE = 1
    SHOW_CHARACTER_DETAILS = 2
    ENABLE_REAL_TIME_NOTES = 3


class Gender(enum.IntEnum):
    """Gender used on hoyolab."""

    unknown = 0
    male = 1
    female = 2
    other = 3


class PartialHoyolabUser(APIModel):
    """Partial hoyolab user from a search result."""

    hoyolab_id: int = pydantic.Field(alias="uid")
    nickname: str
    introduction: str = pydantic.Field(alias="introduce")
    avatar_id: int = pydantic.Field(alias="avatar")
    gender: Gender
    icon: str = pydantic.Field(alias="avatar_url")

    @pydantic.field_validator("nickname")
    @classmethod
    def __remove_highlight(cls, v: str) -> str:
        return re.sub(r"<.+?>", "", v)


class HoyolabUserCertification(APIModel):
    """Hoyolab user certification.

    For example artist's type is 2.
    """

    icon_url: typing.Optional[str] = None
    description: typing.Optional[str] = pydantic.Field(alias="desc", default=None)
    type: int


class HoyolabUserLevel(APIModel):
    """Hoyolab user level."""

    level: int
    exp: int
    level_desc: str
    bg_color: str
    bg_image: str


class FullHoyolabUser(PartialHoyolabUser):
    """Full hoyolab user.

    Not actually full, but most of the data is useless.
    """

    certification: typing.Optional[HoyolabUserCertification] = None
    level: typing.Optional[HoyolabUserLevel] = None
    pendant_url: str = pydantic.Field(alias="pendant")
    bg_url: typing.Optional[str] = None
    pc_bg_url: typing.Optional[str] = None


class RecordCard(GenshinAccount):
    """Hoyolab record card."""

    def __new__(cls, **kwargs: typing.Any) -> RecordCard:
        """Create the appropriate record card."""
        game_id = kwargs.get("game_id", 0)
        if game_id == 1:
            cls = HonkaiRecordCard
        elif game_id == 2:
            cls = GenshinRecordCard
        elif game_id == 6:
            cls = StarRailRecodeCard
        elif game_id == 8:
            cls = ZZZRecordCard

        return super().__new__(cls)  # type: ignore

    game_id: int
    game_biz: str = ""
    game_name: str
    game_logo: str = pydantic.Field(alias="logo")
    uid: int = pydantic.Field(alias="game_role_id")

    data: typing.Sequence[RecordCardData]
    settings: typing.Sequence[RecordCardSetting] = pydantic.Field(alias="data_switches")

    public: bool = pydantic.Field(alias="is_public")
    background_image: str
    has_uid: bool = pydantic.Field(alias="has_role")
    url: str


class GenshinRecordCard(RecordCard):
    """Genshin record card."""

    @property
    def game(self) -> types.Game:
        return types.Game.GENSHIN

    @property
    def days_active(self) -> int:
        return int(self.data[0].value)

    @property
    def characters(self) -> int:
        return int(self.data[1].value)

    @property
    def achievements(self) -> int:
        return int(self.data[2].value)

    @property
    def spiral_abyss(self) -> str:
        return self.data[3].value


class HonkaiRecordCard(RecordCard):
    """Honkai record card."""

    @property
    def game(self) -> types.Game:
        return types.Game.HONKAI

    @property
    def days_active(self) -> int:
        return int(self.data[0].value)

    @property
    def stigmata(self) -> int:
        return int(self.data[1].value)

    @property
    def battlesuits(self) -> int:
        return int(self.data[2].value)

    @property
    def outfits(self) -> int:
        return int(self.data[3].value)


class StarRailRecodeCard(RecordCard):
    """Star rail record card."""

    @property
    def game(self) -> types.Game:
        return types.Game.STARRAIL

    @property
    def days_active(self) -> int:
        return int(self.data[0].value)

    @property
    def characters(self) -> int:
        return int(self.data[1].value)

    @property
    def achievements(self) -> int:
        return int(self.data[2].value)

    @property
    def chests(self) -> int:
        return int(self.data[3].value)


class ZZZRecordCard(RecordCard):
    """ZZZ record card."""

    @property
    def game(self) -> types.Game:
        return types.Game.ZZZ

    @property
    def days_active(self) -> int:
        return int(self.data[0].value)

    @property
    def inter_knot_reputation(self) -> str:
        return self.data[1].value

    @property
    def agents_recruited(self) -> int:
        return int(self.data[2].value)

    @property
    def bangboo_obtained(self) -> int:
        return int(self.data[3].value)
