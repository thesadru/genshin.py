"""Base hoyolab APIModels."""
from __future__ import annotations

import enum
import re
import typing

from genshin.models.model import Aliased, APIModel

__all__ = [
    "GenshinAccount",
    "RecordCardData",
    "RecordCardSetting",
    "RecordCard",
    "Gender",
    "SearchUser",
]


class GenshinAccount(APIModel):
    """Genshin account."""

    uid: int = Aliased("game_uid")
    level: int
    nickname: str
    server: str = Aliased("region")
    server_name: str = Aliased("region_name")


class RecordCardData(APIModel):
    """Data entry of a record card."""

    name: str
    value: str


class RecordCardSetting(APIModel):
    """Privacy setting of a record card."""

    id: int = Aliased("switch_id")
    description: str = Aliased("switch_name")
    public: bool = Aliased("is_public")


class RecordCard(GenshinAccount):
    """Hoyolab record card."""

    def __new__(cls, **kwargs: typing.Any) -> RecordCard:
        """Create the appropriate record card."""
        from .genshin import GenshinRecordCard
        from .honkai import HonkaiRecordCard

        if kwargs["game_id"] == 1:
            cls = HonkaiRecordCard
        elif kwargs["game_id"] == 2:
            cls = GenshinRecordCard
        else:
            cls = RecordCard

        return super().__new__(cls)

    uid: int = Aliased("game_role_id")

    data: typing.Sequence[RecordCardData]
    settings: typing.Sequence[RecordCardSetting] = Aliased("data_switches")

    public: bool = Aliased("is_public")
    background_image: str
    has_uid: bool = Aliased("has_role")
    url: str

    def as_dict(self) -> typing.Dict[str, typing.Any]:
        """Return data as a dictionary."""
        return {d.name: (int(d.value) if d.value.isdigit() else d.value) for d in self.data}


class Gender(enum.IntEnum):
    """Gender used on hoyolab."""

    unknown = 0
    male = 1
    female = 2
    other = 3


class SearchUser(APIModel):
    """User from a search result."""

    hoyolab_uid: int = Aliased("uid")
    nickname: str = Aliased(validator=lambda v: re.sub(r"<.+?>", "", v))
    introduction: str = Aliased("introduce")
    avatar_id: int = Aliased("avatar")
    gender: Gender
    icon: str = Aliased("avatar_url")
