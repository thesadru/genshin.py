"""Honkai hoyolab models."""

from genshin import types

from . import record


class HonkaiRecordCard(record.RecordCard):
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
