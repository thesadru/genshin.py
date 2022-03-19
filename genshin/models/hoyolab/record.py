"""Base hoyolab APIModels."""
from __future__ import annotations

import enum
import re
import typing

from genshin import types
from genshin.models.model import Aliased, APIModel

__all__ = [
    "Gender",
    "GenshinAccount",
    "RecordCard",
    "RecordCardData",
    "RecordCardSetting",
    "SearchUser",
]


class GenshinAccount(APIModel):
    """Genshin account."""

    game_biz: str
    uid: int = Aliased("game_uid")
    level: int
    nickname: str
    server: str = Aliased("region")
    server_name: str = Aliased("region_name")

    @property
    def game(self) -> types.Game:
        if "hk4e" in self.game_biz:
            return types.Game.GENSHIN
        elif "bh3" in self.game_biz:
            return types.Game.HONKAI
        else:
            return types.Game(self.game_biz)


class RecordCardData(APIModel):
    """Data entry of a record card."""

    name: str
    value: str


class RecordCardSetting(APIModel):
    """Privacy setting of a record card."""

    id: int = Aliased("switch_id")
    description: str = Aliased("switch_name")
    public: bool = Aliased("is_public")


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


class RecordCard(GenshinAccount):
    """Hoyolab record card."""

    def __new__(cls, **kwargs: typing.Any) -> RecordCard:
        """Create the appropriate record card."""
        game_id = kwargs.get("game_id", 0)
        if game_id == 1:
            cls = HonkaiRecordCard
        elif game_id == 2:
            cls = GenshinRecordCard

        return super().__new__(cls)

    game_id: int
    game_biz: str = ""
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
