"""Modified pydantic model."""

from __future__ import annotations

import abc
import datetime
import typing
from typing import Annotated

import pydantic

from genshin.constants import CN_TIMEZONE

__all__ = ["APIModel", "Aliased", "Unique"]


class APIModel(pydantic.BaseModel):
    """Modified pydantic model."""

    model_config: pydantic.ConfigDict = pydantic.ConfigDict(arbitrary_types_allowed=True)  # type: ignore


class Unique(abc.ABC):
    """A hashable model with an id."""

    id: int

    def __int__(self) -> int:
        return hash(self.id)

    def __hash__(self) -> int:
        return hash(self.id)


def Aliased(
    alias: typing.Optional[str] = None,
    default: typing.Any = None,
    **kwargs: typing.Any,
) -> typing.Any:
    """Create an aliased field."""
    return pydantic.Field(default, alias=alias, **kwargs)


def add_timezone(value: datetime.datetime) -> datetime.datetime:
    return value.astimezone(CN_TIMEZONE)


def convert_datetime(value: typing.Optional[typing.Mapping[str, typing.Any]]) -> typing.Optional[datetime.datetime]:
    if value:
        return datetime.datetime(**value)
    return None


DateTimeField = Annotated[datetime.datetime, pydantic.AfterValidator(add_timezone)]
DateTime = Annotated[datetime.datetime, pydantic.BeforeValidator(convert_datetime)]
