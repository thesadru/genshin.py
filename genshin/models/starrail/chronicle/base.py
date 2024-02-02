"""Starrail Chronicle Base Model."""

import datetime

from genshin.models.model import APIModel


class PartialTime(APIModel):
    """Partial time model."""

    year: int
    month: int
    day: int
    hour: int
    minute: int

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime(self.year, self.month, self.day, self.hour, self.minute)
