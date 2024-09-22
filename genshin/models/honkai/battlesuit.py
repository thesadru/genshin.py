"""Honkai battlesuit model."""

import logging
import re

import pydantic

from genshin.models.model import Aliased, APIModel, Unique

from .constants import BATTLESUIT_IDENTIFIERS

__all__ = ["Battlesuit"]

_LOGGER = logging.getLogger(__name__)

BATTLESUIT_TYPES = {
    "ShengWu": "BIO",
    "JiXie": "MECH",
    "YiNeng": "PSY",
    "LiangZi": "QUA",
    "XuShu": "IMG",
    "Xingchen": "SD",
}
ICON_BASE = "https://upload-os-bbs.mihoyo.com/game_record/honkai3rd/global/SpriteOutput/"


class Battlesuit(APIModel, Unique):
    """Represents a battlesuit without equipment or level."""

    id: int
    name: str
    rarity: int = Aliased("star")
    closeup_icon_background: str = Aliased("avatar_background_path")
    tall_icon: str = Aliased("figure_path")
    banner_art: str = Aliased("image_path")

    @pydantic.field_validator("tall_icon")
    def __autocomplete_figpath(cls, tall_icon: str, info: pydantic.ValidationInfo) -> str:
        """figure_path is empty for gamemode endpoints, and cannot be inferred from other fields."""
        if tall_icon:
            # might as well just update the BATTLESUIT_IDENTIFIERS if we have the data
            if info.data["id"] not in BATTLESUIT_IDENTIFIERS:
                _LOGGER.debug("Updating BATTLESUIT_IDENTIFIERS with %s", tall_icon)
                BATTLESUIT_IDENTIFIERS[info.data["id"]] = tall_icon.split("/")[-1].split(".")[0]

            return tall_icon

        suit_identifier = BATTLESUIT_IDENTIFIERS.get(info.data["id"])
        return ICON_BASE + f"AvatarTachie/{suit_identifier or 'Unknown'}.png"

    @property
    def character(self) -> str:
        match = re.match(r".*/(\w+C\d+).png", self.tall_icon)
        char_raw = match.group(1) if match else ""

        if "Twin" in char_raw:
            # Rozaliya and Liliya share the same identifier
            return {"TwinC1": "Liliya", "TwinC2": "Rozaliya"}[char_raw]

        # fix mislocalized names
        char_name_raw = char_raw.rsplit("C", 1)[0]
        if char_name_raw == "Fuka":
            return "Fu Hua"

        elif char_name_raw == "Lisushang":
            return "Li Sushang"

        return char_name_raw

    @property
    def rank(self) -> str:
        """Display character rarity with letters ranging from A to SSS, as is done in-game."""
        return ("A", "B", "S", "SS", "SSS")[self.rarity - 1]

    @property
    def _type_cn(self) -> str:
        match = re.match(r".*/Attr(\w+?)(?:Small)?.png", self.closeup_icon_background)
        return match[1] if match else "ShengWu"  # random default just so images keep working

    @property
    def type(self) -> str:
        return BATTLESUIT_TYPES[self._type_cn]

    @property
    def closeup_icon(self) -> str:
        return f"{ICON_BASE}AvatarCardIcons/{60000 + self.id}.png"

    @property
    def icon(self) -> str:
        return f"{ICON_BASE}AvatarIcon/{self.id}.png"

    @property
    def icon_background(self) -> str:
        return f"{ICON_BASE}AvatarIcon/Attr{self._type_cn}.png"

    @property
    def image(self) -> str:
        return f"{ICON_BASE}AvatarCardFigures/{60000 + self.id}.png"

    @property
    def cropped_icon(self) -> str:
        return f"{self.image[:-4]}@1.png"

    @property
    def banner(self) -> str:
        return f"{self.image[:-4]}@2.png"
