from __future__ import annotations

import re
from abc import ABC
from typing import Any, Dict, Literal, Union

from pydantic import BaseModel, Field, root_validator

from ..constants import CHARACTER_NAMES


class GenshinModel(BaseModel):
    """A genshin model"""

    @root_validator(pre=True)
    def __parse_galias(cls, values: Dict[str, Any]):
        """Due to alias being reserved for actual aliases we use a custom alias"""
        aliases = {}
        for name, field in cls.__fields__.items():
            alias = field.field_info.extra.get("galias")
            if alias is not None:
                aliases[alias] = name

        return {aliases.get(name, name): value for name, value in values.items()}


class CharacterIcon(str):
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
    def side(self) -> str:
        return self.create_icon("character_side_icon/UI_AvatarIcon_Side")

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.character_name!r})"


class BaseCharacter(GenshinModel, ABC):
    """A Base character model"""

    id: int
    name: str
    element: str
    rarity: int
    icon: CharacterIcon

    collab: bool = False
    traveler_name: Literal["Aether", "Lumine", ""] = ""

    @property
    def image(self) -> str:
        return self.icon.image

    @property
    def side_icon(self) -> str:
        return self.icon.side

    @root_validator(pre=True)
    def __autocomplete(cls, values: Dict[str, Any]):
        """Complete missing data"""
        id, icon, name = values.get("id"), values.get("icon"), values.get("name")
        if id:
            char = CHARACTER_NAMES.get(id)
            if char is None:
                raise ValueError(f"Invalid character id {id}")
        elif icon:
            icon = CharacterIcon(icon)
            for char in CHARACTER_NAMES.values():
                if char.icon_name == icon.character_name:
                    break
            else:
                # missing data for this character
                return values
        elif name:
            for char in CHARACTER_NAMES.values():
                if char.name == name:
                    break
            else:
                # cannot complete values for foreign languages
                return values
        else:
            raise TypeError("Character data incomplete")

        values["id"] = values.get("id") or char.id
        values["icon"] = values.get("icon") or CharacterIcon(char.icon_name)
        values["name"] = values.get("name") or char.name
        values["element"] = values.get("element") or char.element
        values["rarity"] = values.get("rarity") or char.rarity

        if values["rarity"] > 100:
            values["rarity"] -= 100
            values["collab"] = True

        if values["id"] == 10000005:
            values["traveler_name"] = "Aether"
        elif values["id"] == 10000007:
            values["traveler_name"] = "Lumine"

        return values


class PartialCharacter(BaseCharacter):
    """A character without any equipment"""

    level: int
    friendship: int = Field(galias="fetter")
    constellation: int = Field(0, galias="activated_constellation_num")
