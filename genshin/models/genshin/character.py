"""Genshin character model."""

import logging
import re
import typing

import pydantic

from genshin.models.model import APIModel, Unique

from .constants import CHARACTER_NAMES, DBChar

__all__ = ["BaseCharacter"]

_LOGGER = logging.getLogger(__name__)

ICON_BASE = "https://upload-os-bbs.mihoyo.com/game_record/genshin/"


def _parse_icon(icon: typing.Union[str, int]) -> str:
    if isinstance(icon, int):
        char = CHARACTER_NAMES.get(icon)
        if char is None:
            raise ValueError(f"Invalid character id {icon}")

        return char.icon_name

    match = re.search(r"UI_AvatarIcon(?:_Side)?_(.*).png", icon)
    if match:
        return match[1]

    return icon


def _create_icon(icon: str, specifier: str, scale: int = 0) -> str:
    if "http" in icon and "genshin" not in icon:
        return icon  # no point in trying to parse invalid urls

    icon_name = _parse_icon(icon)
    return ICON_BASE + f"{specifier}_{icon_name}{f'@{scale}x' if scale else ''}.png"


def _get_db_char(
    id: typing.Optional[int] = None,
    name: typing.Optional[str] = None,
    icon: typing.Optional[str] = None,
    element: typing.Optional[str] = None,
    rarity: typing.Optional[int] = None,
) -> DBChar:
    """Get the appropriate DBChar object from specific fields."""
    if id and id in CHARACTER_NAMES:
        char = CHARACTER_NAMES[id]
        if name is not None:
            char = char._replace(name=name)

        return char

    if icon and "genshin" in icon:
        icon_name = _parse_icon(icon)

        for char in CHARACTER_NAMES.values():
            if char.icon_name == icon_name:
                if name is not None:
                    char = char._replace(name=name)

                return char

        # might as well just update the CHARACTER_NAMES if we have all required data
        if id and name and icon and element and rarity:
            char = DBChar(id, icon_name, name, element, rarity, guessed=True)
            _LOGGER.debug("Updating CHARACTER_NAMES with %s", char)
            CHARACTER_NAMES[char.id] = char
            return char

        return DBChar(id or 0, icon_name, name or icon_name, element or "Anemo", rarity or 5, guessed=True)

    if name:
        for char in CHARACTER_NAMES.values():
            if char.name == name:
                return char

        return DBChar(id or 0, icon or name, name, element or "Anemo", rarity or 5, guessed=True)

    raise ValueError("Character data incomplete")


class BaseCharacter(APIModel, Unique):
    """Base character model."""

    id: int
    name: str
    element: str
    rarity: int
    icon: str

    collab: bool = False

    @pydantic.root_validator(pre=True)
    def __autocomplete(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """Complete missing data."""
        id, name, icon, element, rarity = (values.get(x) for x in ("id", "name", "icon", "element", "rarity"))

        char = _get_db_char(id, name, icon, element, rarity)
        icon = _create_icon(char.icon_name, "character_icon/UI_AvatarIcon")

        values["id"] = char.id
        values["name"] = char.name
        values["element"] = char.element
        values["rarity"] = char.rarity

        if values.get("icon"):
            # there is an icon
            if "genshin" in values["icon"] or char.id != 0:
                # side icon OR corrupted icon completion should be able to fix
                values["icon"] = icon
        else:
            # there wasn't an icon so no need for special handling
            values["icon"] = icon

        # collab characters are stored as 105 to show a red background
        if values["rarity"] > 100:
            values["rarity"] -= 100
            values["collab"] = True

        elif values["id"] == 10000062:
            # sometimes Aloy has 5* if no background is needed
            values["collab"] = True

        return values

    @property
    def image(self) -> str:
        return _create_icon(self.icon, "character_image/UI_AvatarIcon", scale=2)

    @property
    def side_icon(self) -> str:
        return _create_icon(self.icon, "character_side_icon/UI_AvatarIcon_Side")

    @property
    def traveler_name(self) -> str:
        if self.id == 10000005:
            return "Aether"
        elif self.id == 10000007:
            return "Lumine"
        else:
            return ""
