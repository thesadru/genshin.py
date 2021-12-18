from __future__ import annotations

import abc
import re
import warnings
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Union

from pydantic import BaseModel, Field, root_validator, validator
from pydantic.fields import ModelField

from ..constants import (
    BATTLESUIT_NAMES,
    CHARACTER_NAMES,
    DBChar,
    DBSuit,
)

__all__ = [
    "APIModel",
    "Unique",
    "CharacterIcon",
    "BaseCharacter",
    "PartialCharacter",
    "BaseBattlesuit",
    "BattlesuitIcon",
    "Battlesuit",
]

TYPES_TO_CN = {"BIO": "ShengWu", "MECH": "JiXie", "PSY": "YiNeng", "QUA": "LiangZi", "IMG": "XuShu"}
TYPES_FROM_CN = {value: key for key, value in TYPES_TO_CN.items()}


# GENERIC


class APIModel(BaseModel, abc.ABC):
    """Base model for all API response models"""

    # nasty pydantic bug fixed only on the master branch - waiting for pypi release
    if TYPE_CHECKING:
        _mi18n_urls: ClassVar[Dict[str, str]]
        _mi18n: ClassVar[Dict[str, Dict[str, str]]]
    else:
        _mi18n_urls = {
            "bbs": "https://webstatic-sea.mihoyo.com/admin/mi18n/bbs_cn/m11241040191111/m11241040191111-{lang}.json",
        }
        _mi18n = {}

    def __init__(self, **data: Any) -> None:
        """"""
        # clear the docstring for pdoc
        super().__init__(**data)

    @root_validator(pre=True)
    def __parse_galias(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Due to alias being reserved for actual aliases we use a custom alias"""
        aliases = {}
        for name, field in cls.__fields__.items():
            alias = field.field_info.extra.get("galias")
            if alias is not None:
                aliases[alias] = name

        return {aliases.get(name, name): value for name, value in values.items()}

    @root_validator()
    def __parse_timezones(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        for name, field in cls.__fields__.items():
            if isinstance(values.get(name), datetime) and values[name].tzinfo is None:
                offset = field.field_info.extra.get("timezone", 0)
                tzinfo = timezone(timedelta(hours=offset))
                values[name] = values[name].replace(tzinfo=tzinfo)

        return values

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        """Generate a dictionary representation of the model,
        optionally specifying which fields to include or exclude.

        Takes the liberty of also giving properties as fields.
        """
        for name in dir(type(self)):
            clsvalue = getattr(type(self), name)
            if isinstance(clsvalue, property):
                try:
                    value = getattr(self, name)
                except:
                    continue

                if value == "":
                    continue

                self.__dict__[name] = value

        return super().dict(**kwargs)

    def _get_mi18n(self, field: ModelField, lang: str) -> str:
        key = field.field_info.extra.get("mi18n")
        if key not in self._mi18n:
            return field.name

        return self._mi18n[key][lang]

    class Config:
        allow_mutation = False


class Unique(abc.ABC):
    """A hashable model with an id"""

    id: int

    def __int__(self) -> int:
        return self.id

    def __hash__(self) -> int:
        return hash(self.id)


# GENSHIN


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


class BaseCharacter(APIModel, Unique):
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


# HONKAI


class BaseBattlesuit(APIModel, Unique):
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


class BattlesuitIcon(APIModel):
    """Represents all possible image formats for a battlesuit"""

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
        base = "https://upload-os-bbs.mihoyo.com/game_record/honkai3rd/global/SpriteOutput/"
        return base + f"{specifier}{f'@{scale}' if scale else ''}.png"

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


# STATS


class BaseStats(APIModel, abc.ABC):
    def as_dict(self, lang: str = "en-us") -> Dict[str, Any]:
        """Helper function which turns fields into properly named ones"""
        return {
            self._get_mi18n(field, lang): getattr(self, field.name)
            for field in self.__fields__.values()
        }
