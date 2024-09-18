"""Modified pydantic model."""

from __future__ import annotations

import abc
import datetime
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

    @pydantic.root_validator()
    def __parse_timezones(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """Timezones are a pain to deal with so we at least allow a plain hour offset."""
        for name, field in cls.__fields__.items():
            if isinstance(values.get(name), datetime.datetime) and values[name].tzinfo is None:
                timezone = field.field_info.extra.get("timezone", 0)
                if not isinstance(timezone, datetime.timezone):
                    timezone = datetime.timezone(datetime.timedelta(hours=timezone))

                values[name] = values[name].replace(tzinfo=timezone)

        return values

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        """Generate a dictionary representation of the model.

        Takes the liberty of also giving properties as fields.
        """
        for name in dir(type(self)):
            obj = getattr(type(self), name)
            if isinstance(obj, property):
                value = getattr(self, name, _SENTINEL)

                if name[0] == "_" or value is _SENTINEL or value == "":
                    continue

                self.__dict__[name] = value

        return super().dict(**kwargs)

    if not typing.TYPE_CHECKING:

        class Config:
            allow_mutation = False


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
    *,
    timezone: typing.Optional[typing.Union[int, datetime.datetime]] = None,
    **kwargs: typing.Any,
) -> typing.Any:
    """Create an aliased field."""
    if timezone is not None:
        kwargs.update(timezone=timezone)

    return pydantic.Field(default, alias=alias, **kwargs)
