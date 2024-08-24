"""Modified pydantic model."""

from __future__ import annotations

import abc
import datetime
import functools
import typing

import pydantic

from genshin.constants import CN_TIMEZONE

__all__ = ["APIModel", "UTC8Timestamp"]


class APIModel(pydantic.BaseModel, abc.ABC):
    """Modified pydantic model."""

    class Config:
        arbitrary_types_allowed = True


def parse_timezone(value: datetime.datetime, timezone: int | datetime.timezone) -> datetime.datetime:
    """Timezones are a pain to deal with so we at least allow a plain hour offset."""
    if not isinstance(timezone, datetime.timezone):
        timezone = datetime.timezone(datetime.timedelta(hours=timezone))

    return value.replace(tzinfo=timezone)


UTC8Timestamp = typing.Annotated[
    datetime.datetime, pydantic.AfterValidator(functools.partial(parse_timezone, timezone=CN_TIMEZONE))
]
