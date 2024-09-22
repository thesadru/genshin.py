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


class BattlesuitWeapon(Equipment):
    """Battlesuit weapon."""


class FullBattlesuit(battlesuit.Battlesuit):
    """Battlesuit complete with equipped weapon and stigmata."""

    level: int
    weapon: BattlesuitWeapon
    stigmata: typing.Sequence[Stigma] = Aliased("stigmatas")

    @pydantic.model_validator(mode="before")
    def __unnest_char_data(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if isinstance(values.get("character"), typing.Mapping):
            values.update(values["character"])

        values.update(values.get("avatar", {}))

        return values

    @pydantic.field_validator("stigmata")
    def __remove_unequipped_stigmata(cls, value: typing.Sequence[Stigma]) -> typing.Sequence[Stigma]:
        return [stigma for stigma in value if stigma.id != 0]
