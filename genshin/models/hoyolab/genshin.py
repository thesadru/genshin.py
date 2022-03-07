"""Genshin hoyolab models."""

from . import record


class GenshinRecordCard(record.RecordCard):
    """Genshin record card."""

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
