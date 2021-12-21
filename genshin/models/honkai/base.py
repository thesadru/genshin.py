from typing import Any, Dict

from genshin import models
from pydantic import Field, root_validator

__all__ = ["Battlesuit"]

BATTLESUIT_TYPES = {"ShengWu": "BIO", "JiXie": "MECH", "YiNeng": "PSY", "LiangZi": "QUA", "XuShu": "IMG"}

# TODO: Icons


class Battlesuit(models.APIModel, models.Unique):
    """Represents a battlesuit without equipment or level

    Returned through all gamemode endpoints.
    """

    id: int
    name: str
    type: str
    stars: int = Field(galias="star")
    character: str

    @property
    def rank(self) -> str:
        """Rank in-game is displayed with letters ranging from A to SSS, not stars."""
        return ("A", "B", "S", "SS", "SSS")[self.stars - 1]

    @root_validator(pre=True)
    def __autocomplete_icons(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: I don't wanna have anything to do with this
        # PLEASE PLEASE PLEASE I BEG YOU; use properties if you can
        return values
