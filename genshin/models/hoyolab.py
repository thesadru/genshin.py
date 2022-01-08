import re
from enum import Enum, IntEnum
from typing import Any, Dict, Optional

from pydantic import Field, validator
from pydantic.class_validators import root_validator

from genshin import models

__all__ = [
    "Game",
    "GameAccount",
    "Gender",
    "SearchUser",
]


class Game(Enum):
    genshin = "Genshin Impact"
    honkai = "Honkai Impact"


class GameAccount(models.APIModel):
    """A Genshin or Honkai account"""

    uid: int = Field(galias="game_uid")
    level: int
    nickname: str
    server: str = Field(galias="region")
    server_name: str = Field(galias="region_name")
    game: Optional[Game]

    @root_validator(pre=True)
    def __get_game(cls, values: Dict[str, Any]):
        # TODO: Should we instead split this into two classes?
        games = {
            "bh3": Game.honkai,
            "hk4e": Game.genshin,
        }
        # only game_biz for accounts, only game_id for record cards
        identifier = values.get("game_biz") or values.get("game_id")
        if isinstance(identifier, int):
            values["game"] = list(games.values())[identifier - 1]
        elif isinstance(identifier, str):
            identifier = identifier.split("_")[0]
            values["game"] = games[identifier]
        else:
            pass  # Probably new game released, shouldn't break anything though

        return values


class Gender(IntEnum):
    unknown = 0
    male = 1
    female = 2
    other = 3


class SearchUser(models.APIModel):
    """A user from a search result"""

    hoyolab_uid: int = Field(galias="uid")
    nickname: str
    introduction: str = Field(galias="introduce")
    avatar_id: int = Field(galias="avatar")
    gender: Gender
    icon: str = Field(galias="avatar_url")

    @validator("nickname")
    def __remove_tag(cls, v: str) -> str:
        return re.sub(r"<.+?>", "", v)
