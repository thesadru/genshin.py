"""Genshin character model."""

import re
import typing
import warnings

import pydantic

from genshin.models.model import APIModel, Unique

from .constants import CHARACTER_NAMES, DBChar

__all__ = ["BaseCharacter"]

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
    icon_name = _parse_icon(icon)
    return ICON_BASE + f"{specifier}_{icon_name}{f'@{scale}x' if scale else ''}.png"


def _get_db_char(
    id: typing.Optional[int] = None,
    icon: typing.Optional[str] = None,
    name: typing.Optional[str] = None,
) -> DBChar:
    """Get the appropriate DBChar object from specific fields."""
    if id and id in CHARACTER_NAMES:
        return CHARACTER_NAMES[id]

    if icon and "genshin" in icon:
        icon_name = _parse_icon(icon)

        for char in CHARACTER_NAMES.values():
            if char.icon_name == icon_name:
                return char

        warnings.warn(f"Completing data for an unknown character: id={id}, icon={icon_name}, name={name}")
        return DBChar(0, icon_name, icon_name, "Anemo", 5)

    if name:
        for char in CHARACTER_NAMES.values():
            if char.name == name:
                return char

        warnings.warn(f"Completing data for a partial character: id={id}, name={name}")
        return DBChar(0, name, name, "Anemo", 5)

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
        id, icon, name = values.get("id"), values.get("icon"), values.get("name")

        char = _get_db_char(id, icon, name)
        icon = _create_icon(char.icon_name, "character_icon/UI_AvatarIcon")

        values["id"] = values.get("id") or char.id

        if not values.get("icon"):
            # there is an icon
            if "genshin" in (values.get("icon") or ""):
                # there is an icon and it's fine
                values["icon"] = icon

            else:
                # there is an icon but it's corrupted
                if char.id != 0:
                    # since completion succeeded we can fix it
                    values["icon"] = icon
        else:
            # there wasn't an icon so no need for special handling
            values["icon"] = icon

        values["name"] = values.get("name") or char.name
        values["element"] = values.get("element") or char.element
        values["rarity"] = values.get("rarity") or char.rarity

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
