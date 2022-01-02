from genshin import models

__all__ = [
    "GenshinRecordCardSetting",
    "GenshinRecordCard",
]


class GenshinRecordCardSetting(models.BaseRecordCardSetting):
    """Represents a privacy setting of a Genshin record card"""

    _names = {
        1: "Battle Chronicle",
        2: "Character Details",
        3: "Real-Time Notes",
    }


class GenshinRecordCard(models.record.GenericRecordCard[GenshinRecordCardSetting]):
    """Represents a hoyolab record card containing very basic Genshin user info"""

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
