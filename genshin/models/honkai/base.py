import re
import warnings
from typing import Any, Dict

from genshin import models
from pydantic import Field, validator

__all__ = ["Battlesuit"]

BATTLESUIT_TYPES = {
    "ShengWu": "BIO",
    "JiXie": "MECH",
    "YiNeng": "PSY",
    "LiangZi": "QUA",
    "XuShu": "IMG",
}
ICON_BASE = "https://upload-os-bbs.mihoyo.com/game_record/honkai3rd/global/SpriteOutput/"
CHARACTER_TALL_ICONS: Dict[int, str] = {  # TODO: Move to constants?
    101: "KianaC2",
    102: "KianaC1",
    103: "KianaC4",
    104: "KianaC3",
    105: "KianaC6",
    111: "KallenC1",
    112: "KallenC2",
    113: "KianaC5",
    114: "KallenC3",
    201: "MeiC2",
    202: "MeiC3",
    203: "MeiC1",
    204: "MeiC4",
    205: "MeiC5",
    211: "SakuraC1",
    212: "SakuraC2",
    213: "SakuraC3",
    214: "SakuraC4",
    301: "BronyaC1",
    302: "BronyaC2",
    303: "BronyaC3",
    304: "BronyaC4",
    311: "BronyaC5",
    312: "BronyaC6",
    313: "BronyaC7",
    314: "BronyaC8",
    401: "HimekoC1",
    402: "HimekoC2",
    403: "HimekoC3",
    404: "HimekoC4",
    411: "HimekoC5",
    412: "HimekoC6",
    421: "TwinC1",
    422: "TwinC2",
    501: "TheresaC1",
    502: "TheresaC2",
    503: "TheresaC3",
    504: "TheresaC4",
    506: "TheresaC6",
    511: "TheresaC5",
    601: "FukaC1",
    602: "FukaC2",
    603: "FukaC3",
    604: "FukaC4",
    611: "FukaC5",
    612: "FukaC6",
    702: "RitaC2",
    703: "RitaC3",
    704: "RitaC4",
    705: "RitaC5",
    711: "SeeleC1",
    712: "SeeleC2",
    713: "SeeleC3",
    801: "DurandalC1",
    802: "DurandalC2",
    803: "DurandalC3",
    901: "AsukaC1",
    2101: "FischlC1",
    2201: "ElysiaC1",
    2301: "MobiusC1",
    2401: "RavenC1",
    2501: "CaroleC1",
}


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

        suit_identifier = CHARACTER_TALL_ICONS.get(values["id"], None)
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
