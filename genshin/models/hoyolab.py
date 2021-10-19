from typing import List

from pydantic import Field

from .base import GenshinModel


class GenshinAccount(GenshinModel):
    """A genshin account"""

    uid: int = Field(galias="game_uid")
    level: int
    nickname: str
    server: str = Field(galias="region")
    server_name: str = Field(galias="region_name")


class RecordCardData(GenshinModel):
    """A data entry of a record card"""

    name: str
    value: str


class RecordCard(GenshinAccount):
    """A genshin record card containing very basic user info"""

    uid: int = Field(galias="game_role_id")

    data: List[RecordCardData]

    # unknown meaning
    background_image: str
    has_uid: bool = Field(galias="has_role")
    public: bool = Field(galias="is_public")

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

    @property
    def html_url(self) -> str:
        """The html url"""
        return f"https://webstatic-sea.hoyolab.com/app/community-game-records-sea/index.html?uid={self.uid}#/ys"

    def as_dict(self, lang: str = "en-us"):
        """Helper function which turns fields into properly named ones"""
        assert lang == "en-us", "Other languages not yet implemented"

        return {d.name: (int(d.value) if d.value.isdigit() else d.value) for d in self.data}


class SearchUser(GenshinModel):
    """A user from a search result"""

    hoyolab_uid: int = Field(galias="uid")
    nickname: str
    introduction: str = Field(galias="introduce")
    avatar_id: int = Field(galias="avatar")
    gender: int
    icon: str = Field(galias="avatar_url")
