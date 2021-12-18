from typing import Any, Dict, List

from pydantic import Field, root_validator

from ..base import APIModel, BaseBattlesuit, Battlesuit, Unique


class Equipment(APIModel, Unique):
    """Represents a stigma or weapon."""

    # Actually works for both weapons and stigmata as the API returns the same data for them

    id: int
    name: str
    rarity: int  # Equipment rarity *is* done with stars
    max_rarity: int
    icon: str


class _NestedBattlesuit(BaseBattlesuit):
    """Hack to unnest battlesuit data (using root_validator) before autocompleting (also using root_validator)
    by manipulating the order of the validators through multiple inheritance.
    """

    # TODO: perhaps figure out some better way of doing this

    @root_validator(pre=True)
    def __unnest_char_data(cls, values: Dict[str, Any]):
        values.update(values.pop("avatar"))
        return values


class FullBattlesuit(Battlesuit, _NestedBattlesuit):
    """Represents a battlesuit complete with equipped weapon and stigmata.

    Returned through the character endpoint.
    """

    level: int
    weapon: Equipment
    stigmata: List[Equipment] = Field(galias="stigmatas")
