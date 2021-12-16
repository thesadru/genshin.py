from __future__ import annotations

import abc
import re
import warnings
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Union

from pydantic import BaseModel, Field, root_validator
from pydantic.fields import ModelField

from ..constants import CHARACTER_NAMES, DBChar

__all__ = [
    "GenshinModel",
    "Unique",
    "CharacterIcon",
    "BaseCharacter",
    "PartialCharacter",
]


class GenshinModel(BaseModel, abc.ABC):
    """A genshin model"""

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
    def __parse_galias(cls, values: Dict[str, Any]):
        """Due to alias being reserved for actual aliases we use a custom alias"""
        aliases = {}
        for name, field in cls.__fields__.items():
            alias = field.field_info.extra.get("galias")
            if alias is not None:
                aliases[alias] = name

        return {aliases.get(name, name): value for name, value in values.items()}

    @root_validator()
    def __parse_timezones(cls, values: Dict[str, Any]):
        for name, field in cls.__fields__.items():
            if isinstance(values.get(name), datetime) and values[name].tzinfo is None:
                offset = field.field_info.extra.get("timezone", 0)
                tzinfo = timezone(timedelta(hours=offset))
                values[name] = values[name].replace(tzinfo=tzinfo)

        return values

    def dict(self, **kwargs) -> Dict[str, Any]:
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


class CharacterIcon:
    """A character's icon"""

    character_name: str

    def __init__(self, icon: Union[str, int]) -> None:
        if isinstance(icon, int):
            char = CHARACTER_NAMES.get(icon)
            if char is None:
                raise ValueError(f"Invalid character id {icon}")
            self.character_name = char.icon_name
        else:
            match = re.search(r"UI_AvatarIcon(?:_Side)?_(.*).png", icon)
            self.character_name = icon if match is None else match.group(1)

    def create_icon(self, specifier: str, scale: int = 0) -> str:
        base = "https://upload-os-bbs.mihoyo.com/game_record/genshin/"
        return base + f"{specifier}_{self.character_name}{f'@{scale}x' if scale else ''}.png"

    @property
    def icon(self) -> str:
        return self.create_icon("character_icon/UI_AvatarIcon")

    @property
    def image(self) -> str:
        return self.create_icon("character_image/UI_AvatarIcon", scale=2)

    @property
    def side_icon(self) -> str:
        return self.create_icon("character_side_icon/UI_AvatarIcon_Side")

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.character_name!r})"


class BaseCharacter(GenshinModel, Unique):
    """A Base character model"""

    id: int
    name: str
    element: str
    rarity: int
    icon: str

    collab: bool = False

    @root_validator(pre=True)
    def __autocomplete(cls, values: Dict[str, Any]):
        """Complete missing data"""
        partial: bool = False

        id, icon, name = values.get("id"), values.get("icon"), values.get("name")

        if id and id in CHARACTER_NAMES:
            char = CHARACTER_NAMES[id]

        elif icon and "genshin" in icon:
            icon = CharacterIcon(icon)
            for char in CHARACTER_NAMES.values():
                if char.icon_name == icon.character_name:
                    break
            else:
                warnings.warn("Completing data for an unknown character")
                name = icon.character_name
                char = DBChar(0, name, name, "Anemo", 5)

        elif name:
            for char in CHARACTER_NAMES.values():
                if char.name == name:
                    break
            else:
                warnings.warn("Completing data for a partial character")
                partial = True
                char = DBChar(0, name, name, "Anemo", 5)

        else:
            raise ValueError("Character data incomplete")

        values["id"] = values.get("id") or char.id

        # malformed icon handling (in calculation)
        if "genshin" in (values.get("icon") or ""):
            values["icon"] = CharacterIcon(values["icon"]).icon
        elif values.get("icon"):
            if not partial:
                values["icon"] = CharacterIcon(char.icon_name).icon
        else:
            values["icon"] = CharacterIcon(char.icon_name).icon

        values["name"] = values.get("name") or char.name
        values["element"] = values.get("element") or char.element
        values["rarity"] = values.get("rarity") or char.rarity

        if values["rarity"] > 100:
            values["rarity"] -= 100
            values["collab"] = True
        elif values["id"] == 10000062:
            # sometimes Alot has 5* like normal, like cmon
            values["collab"] = True

        return values

    @property
    def image(self) -> str:
        return CharacterIcon(self.icon).image

    @property
    def side_icon(self) -> str:
        return CharacterIcon(self.icon).side_icon

    @property
    def traveler_name(self) -> str:
        if self.id == 10000005:
            return "Aether"
        elif self.id == 10000007:
            return "Lumine"
        else:
            return ""


class PartialCharacter(BaseCharacter):
    """A character without any equipment"""

    level: int
    friendship: int = Field(galias="fetter")
    constellation: int = Field(galias="actived_constellation_num")
