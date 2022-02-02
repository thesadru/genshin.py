import re
import warnings
from typing import Any, Dict

from pydantic import Field, validator

from genshin import models
from genshin.constants import BATTLESUIT_IDENTIFIERS

__all__ = ["Battlesuit"]

BATTLESUIT_TYPES = {
    "ShengWu": "BIO",
    "JiXie": "MECH",
    "YiNeng": "PSY",
    "LiangZi": "QUA",
    "XuShu": "IMG",
}
ICON_BASE = "https://upload-os-bbs.mihoyo.com/game_record/honkai3rd/global/SpriteOutput/"


class Battlesuit(models.APIModel, models.Unique):
    """Represents a battlesuit without equipment or level

    Returned through all gamemode endpoints.
    """

    id: int
    name: str
    rarity: int = Field(alias="star")
    closeup_icon_background: str = Field(alias="avatar_background_path")
    tall_icon: str = Field(alias="figure_path")

    @validator("tall_icon")
    def __autocomplete_figpath(cls, tall_icon: str, values: Dict[str, Any]):
        # figure_path is empty for gamemode endpoints, and cannot be inferred from other fields
        if tall_icon:
            return tall_icon

        suit_identifier = BATTLESUIT_IDENTIFIERS.get(values["id"])
        if not suit_identifier:
            warnings.warn("Autocompleting data for a battlesuit that isn't (yet) in our database.")
        return ICON_BASE + f"AvatarTachie/{suit_identifier or 'Unknown'}.png"

    @property
    def character(self) -> str:
        match = re.match(r".*/(\w+C\d+).png", self.tall_icon)
        char_raw = match.group(1) if match else ""
        if "Twin" in char_raw:
            # fsr Roza and Lili share the same identifier so we'll have to manually parse the two
            return {"TwinC1": "Liliya", "TwinC2": "Rozaliya"}[char_raw]

        char_name_raw = char_raw.rsplit("C", 1)[0]
        # fix mislocalized names (currently only one)
        return {
            "Fuka": "Fu Hua",  # jp -> en
        }.get(char_name_raw, char_name_raw)

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
