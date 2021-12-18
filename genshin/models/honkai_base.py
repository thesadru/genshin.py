# NOTE: For now, I've kept everything apart as it's probably easier to merge later
#       than to separate later, whichever we decide to do.
#       Any file I create, for now, will be prefixed with "honkai_" for this reason,
#       and could later be merged with filed with matching names (without the prefix).

import re
import warnings
from typing import Any, ClassVar, Dict, Union

from pydantic import Field, root_validator, validator

from .base import GenshinModel, Unique
from ..constants import BATTLESUIT_NAMES, DBSuit

# I'll still just be inheriting from GenshinModel as base, as it works fine;
# I'll similarly stick to using Field(galias=...) for further implementation details.

__all__ = (
    "BaseBattlesuit",
    "BattlesuitIcon",
    "Battlesuit",
)


TYPES_TO_CN = {"BIO": "ShengWu", "MECH": "JiXie", "PSY": "YiNeng", "QUA": "LiangZi", "IMG": "XuShu"}
TYPES_FROM_CN = {value: key for key, value in TYPES_TO_CN.items()}


class BaseBattlesuit(GenshinModel, Unique):
    """A base battlesuit model"""

    id: int
    name: str
    type: str
    rank: str = Field(galias="star")
    character: str

    @validator("rank", pre=True)
    def __fix_rank(cls, star: Union[int, str]) -> str:
        """Rank in-game is displayed with letters ranging from A to SSS, not stars."""
        if isinstance(star, int):
            return ("A", "B", "S", "SS", "SSS")[star - 1]
        return star


class BattlesuitIcon(GenshinModel):
    """Represents all possible image formats for a battlesuit"""

    base: ClassVar = "https://upload-os-bbs.mihoyo.com/game_record/honkai3rd/global/SpriteOutput/"

    icon_name: str
    battlesuit_id: int
    battlesuit_type: str

    @validator("battlesuit_type")
    def __type_to_cn(cls, type: str):
        if type in TYPES_FROM_CN:
            return type
        elif type in TYPES_TO_CN:
            return TYPES_TO_CN[type]
        else:
            raise ValueError("battlesuit_type must be a valid localized or CN type")

    def create_image(self, specifier: str, scale: int = 0) -> str:
        return self.base + f"{specifier}{f'@{scale}' if scale else ''}.png"

    @property
    def banner(self):
        """A wide, banner-like image of the battlesuit."""
        return self.create_image(f"AvatarCardFigures/{60000 + self.battlesuit_id}", scale=2)

    @property
    def cropped_icon(self):
        """A square image showing the battlesuit's upper body."""
        return self.create_image(f"AvatarCardFigures/{60000 + self.battlesuit_id}", scale=1)

    @property
    def image(self):
        """An image of the full battlesuit from the thighs up."""
        return self.create_image(f"AvatarCardFigures/{60000 + self.battlesuit_id}")

    @property
    def tall_icon(self):
        """A thin but tall, cropped image showing most of the battlesuit."""
        return self.create_image(f"AvatarTachie/{self.icon_name}")

    @property
    def icon(self):
        """The battlesuit's head cropped into a slanted frame, as displayed in the in-game Valkyrie menu.
        Meant to be overlayed in front of `self.icon_background`.
        """
        return self.create_image(f"AvatarIcon/{self.battlesuit_id}")

    @property
    def icon_background(self):
        """The background colored after the battlesuit's type cropped into a slanted frame.
        Meant to be layered behind `self.icon`.
        """
        return self.create_image(f"AvatarIcon/Attr{self.battlesuit_type}")

    @property
    def closeup_icon(self):
        """An extremely cropped rectangular image showing only the battlesuit's head.
        Meant to be layered in front of `self.closeup_icon_background`.
        """
        return self.create_image(f"AvatarCardIcons/{60000 + self.battlesuit_id}")

    @property
    def closeup_icon_background(self):
        """The background colored after the battlesuit's type cropped into a rectangular frame.
        Meant to be layered behind `self.closeup_icon`.
        """
        return self.create_image(f"AvatarCardIcons/Attr{self.battlesuit_type}Small")


class Battlesuit(BaseBattlesuit):
    """Represents a battlesuit without equipment or level

    Returned through all gamemode endpoints.
    """

    icon_data: BattlesuitIcon

    @root_validator(pre=True)
    def __autocomplete(cls, values: Dict[str, Any]):
        """Complete missing data"""
        id, name = values.get("id"), values.get("name")

        if id:
            id = int(id)
            if id in BATTLESUIT_NAMES:
                suit = BATTLESUIT_NAMES[id]

        elif name:
            for suit in BATTLESUIT_NAMES.values():
                if suit.name == name:
                    break
            else:
                warnings.warn("Completing data for a partial battlesuit")
                suit = DBSuit(0, name, f"{name}C1", "???", "BIO", "A")

        else:
            raise ValueError("Character data incomplete")

        values["id"] = values.get("id") or suit.id
        values["name"] = values.get("name") or suit.name
        values["type"] = values.get("type") or suit.type
        values["rank"] = values.get("rank") or suit.base_rank

        pat = r"Attr(\w+?)(?:Small)?.png"
        match = re.match(pat, values["avatar_background_path"]) or re.match(
            pat, values["oblique_avatar_background_path"]
        )
        values["type"] = suit.type if match is None else TYPES_FROM_CN[match[1]]

        match = re.search(r"/(\w+C\d+).png", values["figure_path"])
        values["icon_data"] = BattlesuitIcon(
            icon_name=suit.icon_name if match is None else match[1],
            battlesuit_id=values["id"],
            battlesuit_type=values["type"],
        )

        values["character"] = suit.character_name
        return values

    @property
    def image(self):
        """An image of the full battlesuit from the thighs up."""
        return self.icon_data.image

    @property
    def banner(self):
        """A wide, banner-like image of the battlesuit."""
        return self.icon_data.banner

    @property
    def icon(self):
        """The battlesuit's head cropped into a slanted frame, as displayed in the in-game Valkyrie menu."""
        return self.icon_data.icon
