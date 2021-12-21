import re
import warnings
from typing import Any, Dict, Union

from pydantic import Field, root_validator, validator

from genshin.constants import CHARACTER_NAMES, DBChar
from genshin.models import base

__all__ = ["CharacterIcon", "BaseCharacter", "PartialCharacter"]


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


class BaseCharacter(base.APIModel, base.Unique):
    """A Base character model"""

    id: int
    name: str
    element: str
    rarity: int
    icon: str

    collab: bool = False

    @root_validator(pre=True)
    def __autocomplete(cls, values: Dict[str, Any]) -> Dict[str, Any]:
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
