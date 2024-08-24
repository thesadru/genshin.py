"""Honkai battlesuit model."""

import logging
import re

import pydantic

from genshin.models.model import APIModel

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


class Battlesuit(APIModel):
    """Represents a battlesuit without equipment or level."""

    id: int
    name: str
    rarity: int = pydantic.Field(alias="star")
    closeup_icon_background: str = pydantic.Field(alias="avatar_background_path")
    tall_icon: str = pydantic.Field(alias="figure_path")
    banner_art: str = pydantic.Field(alias="image_path")

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
