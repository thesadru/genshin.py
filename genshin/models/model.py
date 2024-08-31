"""Modified pydantic model."""

from __future__ import annotations

import abc
import datetime
import sys
import types
import typing

if typing.TYPE_CHECKING:
    import pydantic.v1 as pydantic
    from pydantic.v1.fields import ModelField
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
        import pydantic

import genshin.constants as genshin_constants

__all__ = ["APIModel", "Aliased", "Unique"]

_SENTINEL = object()


class APIModel(pydantic.BaseModel, abc.ABC):
    """Modified pydantic model."""

    # nasty pydantic bug fixed only on the master branch - waiting for pypi release
    if typing.TYPE_CHECKING:
        _mi18n: typing.ClassVar[typing.Dict[str, typing.Dict[str, str]]]
    else:
        _mi18n = {}

    lang: str = "UNKNOWN"

    def __init__(self, _frame: int = 1, **data: typing.Any) -> None:
        """"""
        from genshin.client.components import base as client_base

        lang = data.pop("lang", None)

        if lang is None:
            frames = [sys._getframe(_frame)]
            while _frame <= 100:  # ensure we give up in a reasonable amount of time
                _frame += 1
                try:
                    frame = sys._getframe(_frame)
                except ValueError:
                    break

                if frame.f_code.co_name == "__init__" and frame.f_code.co_filename == __file__:
                    frames.append(frame)
                    break

            for frame in frames:
                if frame.f_code.co_name == "<listcomp>":
                    frame = typing.cast("types.FrameType", frame.f_back)
                    assert frame

                if isinstance(frame.f_locals.get("lang"), str):
                    lang = frame.f_locals["lang"]

                for name, value in frame.f_locals.items():
                    if isinstance(value, (APIModel, client_base.BaseClient)):
                        lang = value.lang

                if lang:
                    break

                # validator, it's a skipper
                if isinstance(frame.f_locals.get("cls"), type) and issubclass(frame.f_locals["cls"], APIModel):
                    continue

            else:
                raise Exception("lang not found")

        object.__setattr__(self, "lang", lang)
        super().__init__(**data, lang=lang)

        for name in self.__fields__.keys():
            value = getattr(self, name)
            if isinstance(value, APIModel):
                object.__setattr__(value, "lang", self.lang)

        if self.lang not in genshin_constants.LANGS:
            raise Exception(f"Invalid model lang: {self.lang}")

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

    def _get_mi18n(
        self,
        field: typing.Union[ModelField, str],
        lang: str,
        *,
        default: typing.Optional[str] = None,
    ) -> str:
        """Get localized name of a field."""
        if isinstance(field, str):
            key = field.lower()
            default = default or key
        else:
            if not field.field_info.extra.get("mi18n"):
                raise TypeError(f"{field!r} does not have mi18n.")

            key = field.field_info.extra["mi18n"]
            default = default or field.name

        if key not in self._mi18n:
            return default

        if lang not in self._mi18n[key]:
            raise TypeError(f"mi18n not loaded for {lang}")

        return self._mi18n[key][lang]

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
    mi18n: typing.Optional[str] = None,
    **kwargs: typing.Any,
) -> typing.Any:
    """Create an aliased field."""
    if timezone is not None:
        kwargs.update(timezone=timezone)
    if mi18n is not None:
        kwargs.update(mi18n=mi18n)

    return pydantic.Field(default, alias=alias, **kwargs)
