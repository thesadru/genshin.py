from typing import Any, Dict, List

from genshin import models
from genshin.models.honkai import base
from pydantic import Field, root_validator


class Equipment(models.APIModel, models.Unique):
    """Represents a stigma or weapon."""

    # Actually works for both weapons and stigmata as the API returns the same data for them

    id: int
    name: str
    rarity: int  # Equipment rarity *is* done with stars
    max_rarity: int
    icon: str


class FullBattlesuit(base.Battlesuit):
    """Represents a battlesuit complete with equipped weapon and stigmata.

    Returned through the character endpoint.
    """

    level: int
    weapon: Equipment
    stigmata: List[Equipment] = Field(galias="stigmatas")

    @root_validator(pre=True)
    def __unnest_char_data(cls, values: Dict[str, Any]):
        values.update(values.pop("avatar"))
        return values
