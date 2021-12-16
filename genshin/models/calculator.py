import collections
from typing import Any, Dict, List, NamedTuple

from pydantic import Field, validator

from .base import BaseCharacter, GenshinModel, Unique

__all__ = [
    "CalculatorCharacter",
    "CalculatorWeapon",
    "CalculatorArtifact",
    "CalculatorTalent",
    "CalculatorConsumable",
    "CalculatorArtifactResult",
    "CalculatorResult",
    "CalculatorObject",
]

CALCULATOR_ELEMENTS: Dict[int, str] = {
    1: "Pyro",
    2: "Anemo",
    3: "Geo",
    4: "Dendro",
    5: "Electro",
    6: "Hydro",
    7: "Cryo",
}
CALCULATOR_WEAPON_TYPES: Dict[int, str] = {
    1: "Sword",
    10: "Catalyst",
    11: "Claymore",
    12: "Bow",
    13: "Polearm",
}
CALCULATOR_ARTIFACTS: Dict[int, str] = {
    1: "Flower of Life",
    2: "Plume of Death",
    3: "Sands of Eon",
    4: "Goblet of Eonothem",
    5: "Circlet of Logos",
}


class CalculatorCharacter(BaseCharacter):
    """A character meant to be used with calculators"""

    rarity: int = Field(galias="avatar_level")
    element: str = Field(galias="element_attr_id")
    weapon_type: str = Field(galias="weapon_cat_id")

    max_level: int

    @validator("element")
    def __parse_element(cls, v):
        return CALCULATOR_ELEMENTS[int(v)]

    @validator("weapon_type")
    def __parse_weapon_type(cls, v):
        return CALCULATOR_WEAPON_TYPES[int(v)]


class CalculatorWeapon(GenshinModel, Unique):
    """A weapon meant to be used with calculators"""

    id: int
    name: str
    icon: str
    rarity: int = Field(galias="weapon_level")
    type: str = Field(galias="weapon_cat_id")
    max_level: int

    @validator("type")
    def __parse_weapon_type(cls, v):
        return CALCULATOR_WEAPON_TYPES[int(v)]


class CalculatorArtifact(GenshinModel, Unique):
    """An artifact meant to be used with calculators"""

    id: int
    name: str
    icon: str
    rarity: int = Field(alias="reliquary_level")
    pos: int = Field(alias="reliquary_cat_id")
    max_level: int

    @property
    def pos_name(self) -> str:
        return CALCULATOR_ARTIFACTS[self.pos]


class CalculatorTalent(GenshinModel, Unique):
    """A talent of a character meant to be used with calculators"""

    id: int
    group_id: int
    name: str
    icon: str
    max_level: int


class CalculatorConsumable(GenshinModel, Unique):
    """An item consumed when upgrading"""

    id: int
    name: str
    icon: str
    amount: int = Field(galias="num")


class CalculatorArtifactResult(GenshinModel):
    """A calulation result for a specific artifact"""

    artifact_id: int = Field(alias="reliquary_id")
    list: List[CalculatorConsumable] = Field(alias="id_consume_list")


class CalculatorResult(GenshinModel):
    """A calculation result"""

    character: List[CalculatorConsumable] = Field(galias="avatar_consume")
    weapon: List[CalculatorConsumable] = Field(galias="weapon_consume")
    talents: List[CalculatorConsumable] = Field(galias="avatar_skill_consume")
    artifacts: List[CalculatorArtifactResult] = Field(galias="reliquary_consume")

    @property
    def total(self) -> List[CalculatorConsumable]:
        artifacts = [i for a in self.artifacts for i in a.list]
        combined = self.character + self.weapon + self.talents + artifacts

        grouped: Dict[int, List[CalculatorConsumable]] = collections.defaultdict(list)
        for i in combined:
            grouped[i.id].append(i)

        total = [
            CalculatorConsumable(
                id=x[0].id,
                name=x[0].name,
                icon=x[0].icon,
                amount=sum(i.amount for i in x),
            )
            for x in grouped.values()
        ]

        return total


class CalculatorObject(NamedTuple):
    """An object required in the calculation of required materials"""

    id: int
    current: int
    target: int

    def _serialize(self, prefix: str = "") -> Dict[str, Any]:
        """Serialize the object to a dict"""
        return {
            prefix + "id": self.id,
            prefix + "level_current": self.current,
            prefix + "level_target": self.target,
        }
