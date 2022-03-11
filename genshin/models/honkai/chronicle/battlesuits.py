"""Honkai chronicle battlesuits."""
import re
import typing

import pydantic

from genshin.models.honkai import battlesuit
from genshin.models.model import Aliased, APIModel, Unique


class Equipment(APIModel, Unique):
    """Battlesuit equipment."""

    id: int
    name: str
    rarity: int
    max_rarity: int
    icon: str

    @property
    def type(self) -> str:
        """The type of the equipment"""
        match = re.search(r"/(\w+)Icons/", self.icon)
        base_type = match[1] if match else ""
        if not base_type or base_type == "Stigmata":
            return base_type

        match = re.search(r"/Weapon_([A-Za-z]+?)_", self.icon)
        return match[1] if match else "Weapon"


class Stigma(Equipment):
    """Battlesuit stigma."""


class Weapon(Equipment):
    """Battlesuit weapon."""


class FullBattlesuit(battlesuit.Battlesuit):
    """Battlesuit complete with equipped weapon and stigmata."""

    level: int
    weapon: Weapon
    stigmata: typing.Sequence[Stigma] = Aliased("stigmatas")

    @pydantic.root_validator(pre=True)
    def __unnest_char_data(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        if isinstance(values.get("character"), typing.Mapping):
            values.update(values["character"])

        values.update(values.get("avatar", {}))

        return values

    @pydantic.validator("stigmata")
    def __remove_unequipped_stigmata(cls, value: typing.Sequence[Stigma]) -> typing.Sequence[Stigma]:
        return [stigma for stigma in value if stigma.id != 0]


# shuffle validators around because of nesting
FullBattlesuit.__pre_root_validators__.reverse()
