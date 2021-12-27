from __future__ import annotations

import abc
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, ClassVar, Dict

from pydantic import BaseModel, root_validator
from pydantic.fields import ModelField

__all__ = [
    "APIModel",
    "Unique",
]


class APIModel(BaseModel, abc.ABC):
    """Base model for all API response models"""

    # nasty pydantic bug fixed only on the master branch - waiting for pypi release
    if TYPE_CHECKING:
        _mi18n_urls: ClassVar[Dict[str, str]]
        _mi18n: ClassVar[Dict[str, Dict[str, str]]]
    else:
        _mi18n_urls = {
            "bbs": "https://webstatic-sea.mihoyo.com/admin/mi18n/bbs_cn/m11241040191111/m11241040191111-{lang}.json",
        }
        _mi18n = {}

    def __init__(self, **data: Any) -> None:
        """"""
        # clear the docstring for pdoc
        super().__init__(**data)

    @root_validator(pre=True)
    def __parse_galias(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Due to alias being reserved for actual aliases we use a custom alias"""
        aliases = {}
        for name, field in cls.__fields__.items():
            alias = field.field_info.extra.get("galias")
            if alias is not None:
                aliases[alias] = name

        return {aliases.get(name, name): value for name, value in values.items()}

    @root_validator()
    def __parse_timezones(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        for name, field in cls.__fields__.items():
            if isinstance(values.get(name), datetime) and values[name].tzinfo is None:
                offset = field.field_info.extra.get("timezone", 0)
                tzinfo = timezone(timedelta(hours=offset))
                values[name] = values[name].replace(tzinfo=tzinfo)

        return values

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        """Generate a dictionary representation of the model,
        optionally specifying which fields to include or exclude.

        Takes the liberty of also giving properties as fields.
        """
        for name in dir(type(self)):
            clsvalue = getattr(type(self), name)
            if isinstance(clsvalue, property):
                try:
                    value = getattr(self, name)
                except:
                    continue

                if value == "":
                    continue

                self.__dict__[name] = value

        return super().dict(**kwargs)

    def _get_mi18n(self, field: ModelField, lang: str) -> str:
        key = field.field_info.extra.get("mi18n")
        if key not in self._mi18n:
            return field.name

        return self._mi18n[key][lang]

    class Config:
        allow_mutation = False


class Unique(abc.ABC):
    """A hashable model with an id"""

    id: int

    def __int__(self) -> int:
        return self.id

    def __hash__(self) -> int:
        return hash(self.id)
