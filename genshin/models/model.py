"""Modified pydantic model."""

from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    import pydantic.v1 as pydantic
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
        import pydantic


__all__ = ["APIModel", "Aliased", "Unique"]

_SENTINEL = object()


class APIModel(pydantic.BaseModel, abc.ABC):
    """Modified pydantic model."""


class Unique(abc.ABC):
    """A hashable model with an id."""

    id: int

    def __int__(self) -> int:
        return hash(self.id)

    def __hash__(self) -> int:
        return hash(self.id)


def Aliased(
    alias: typing.Optional[str] = None,
    default: typing.Any = pydantic.main.Undefined,  # type: ignore
    **kwargs: typing.Any,
) -> typing.Any:
    """Create an aliased field."""
    return pydantic.Field(default, alias=alias, **kwargs)
