from __future__ import annotations

import re
from abc import ABC
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator
from pydantic.main import BaseConfig

from ..constants import CHARACTER_NAMES

if TYPE_CHECKING:
    from ..client import GenshinClient

BaseConfig.underscore_attrs_are_private

class CharacterIcon(str):
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
    def icon(self):
        return self.create_icon("character_icon/UI_AvatarIcon")

    @property
    def image(self):
        return self.create_icon("character_image/UI_AvatarIcon", scale=2)

    @property
    def side(self):
        return self.create_icon("character_side_icon/UI_AvatarIcon_Side")

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.character_name!r})"


class BaseCharacter(BaseModel, ABC):
    """A Base character model which autocompletes every static field"""

    id: int = Field(None)
    name: str = Field(None)
    element: str = Field(None)
    rarity: int = Field(None)
    icon: CharacterIcon = Field(None)
    collab: bool = False

    @property
    def image(self) -> str:
        return self.icon.image

    @property
    def side_icon(self) -> str:
        return self.icon.side

    @root_validator
    def __autocomplete(cls, values: Dict[str, Any]):
        # first fetch the char
        id, icon, name = values.get("id"), values.get("icon"), values.get("name")
        if id:
            char = CHARACTER_NAMES[id]
        elif icon:
            char = next(char for char in CHARACTER_NAMES.values() if char.icon_name == icon.character_name)
        elif name:
            char = next((char for char in CHARACTER_NAMES.values() if char.name == name), None)
            # cannot complete values for foreign languages
            if char is None:
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

        return values

    @validator("icon", pre=True)
    def __cast_icon(cls, icon: str):
        return CharacterIcon(icon)

class Character(BaseCharacter):
    """A character without any equipment"""

    level: int
    friendship: int = Field(alias="fetter")
    constellation: int = Field(0, alias="activated_constellation_num")