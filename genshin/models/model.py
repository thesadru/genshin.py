"""Modified pydantic model."""

from __future__ import annotations

import abc
import datetime
import typing

import pydantic
from typing_extensions import Annotated

from genshin.constants import CN_TIMEZONE

__all__ = ["APIModel", "Aliased", "Unique"]


class APIModel(pydantic.BaseModel):
    """Modified pydantic model."""

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)


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
    return value.replace(tzinfo=CN_TIMEZONE)


DateTimeField = Annotated[datetime.datetime, pydantic.AfterValidator(add_timezone)]
