from genshin import models
from pydantic import Field

__all__ = [
    "UserInfo",
    "HonkaiRecordCardSetting",
    "HonkaiRecordCard",
]


class UserInfo(models.APIModel):

    nickname: str
    region: str
    level: int
    icon: str = Field(galias="AvatarUrl")


class HonkaiRecordCardSetting(models.BaseRecordCardSetting):
    """Represents a privacy setting of a Honkai record card"""

    _names = {
        1: "Battle Chronicle",
        2: "Character Details",
    }


class HonkaiRecordCard(models.record.GenericRecordCard[HonkaiRecordCardSetting]):
    """Represents a hoyolab record card containing very basic Honkai user info"""

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
    def outfits(self) -> str:
        return self.data[3].value

    @property
    def html_url(self) -> str:
        """The html url"""
        return f"https://webstatic-sea.hoyolab.com/app/community-game-records-sea/index.html?uid={self.uid}#/bh3"
