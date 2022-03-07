"""Modified pydantic model."""
from __future__ import annotations

import abc
import datetime
import typing

import pydantic

__all__ = ["APIModel", "Aliased", "Unique"]

_SENTINEL = object()


class APIModel(pydantic.BaseModel, abc.ABC):
    """Modified pydantic model."""

    def __init__(self, **data: typing.Any) -> None:
        """"""
        # clear the docstring for pdoc
        super().__init__(**data)

    def __init_subclass__(cls) -> None:
        # parse validators
        for name, field in cls.__fields__.items():
            callback = field.field_info.extra.get("validator")
            if callback is not None:
                pre = field.field_info.extra.get("validator_pre", False)
                validator = pydantic.class_validators.Validator(callback, pre=pre)
                cls.__validators__.setdefault(name, []).append(validator)  # type: ignore

    @pydantic.root_validator(pre=True)
    def __parse_galias(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """Due to alias being reserved for actual aliases we use a custom alias."""
        aliases: typing.Dict[str, str] = {}
        for name, field in cls.__fields__.items():
            alias = field.field_info.extra.get("galias")
            if alias is not None:
                aliases[alias] = name

        return {aliases.get(name, name): value for name, value in values.items()}

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

                if value is _SENTINEL or value == "":
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
        return self.id

    def __hash__(self) -> int:
        return hash(self.id)


def Aliased(
    galias: typing.Optional[str] = None,
    default: typing.Any = pydantic.main.Undefined,  # type: ignore
    *,
    timezone: typing.Optional[typing.Union[int, datetime.datetime]] = None,
    mi18n: typing.Optional[str] = None,
    validator: typing.Optional[typing.Callable[[typing.Any], typing.Any]] = None,
    pre: bool = False,
    **kwargs: typing.Any,
) -> typing.Any:
    """Create an aliased field."""
    if galias is not None:
        kwargs.update(galias=galias)
    if timezone is not None:
        kwargs.update(timezone=timezone)
    if mi18n is not None:
        kwargs.update(mi18n=mi18n)
    if validator is not None:
        kwargs.update(validator=validator, validator_pre=pre)

    return pydantic.Field(default, **kwargs)
