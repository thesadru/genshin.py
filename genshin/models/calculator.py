import collections
from typing import Any, Dict, List, Literal, NamedTuple, Union

from pydantic import Field, validator

from .base import BaseCharacter, GenshinModel, Unique

__all__ = [
    "CALCULATOR_ELEMENTS",
    "CALCULATOR_WEAPON_TYPES",
    "CALCULATOR_ARTIFACTS",
    "CalculatorCharacter",
    "CalculatorWeapon",
    "CalculatorArtifact",
    "CalculatorTalent",
    "CalculatorCharacterDetails",
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
    level: int = Field(0, galias="level_current")
    max_level: int

    @validator("element", pre=True)
    def __parse_element(cls, v: Any) -> str:
        if isinstance(v, str):
            return v

        return CALCULATOR_ELEMENTS[int(v)]

    @validator("weapon_type", pre=True)
    def __parse_weapon_type(cls, v: Any) -> str:
        if isinstance(v, str):
            return v

        return CALCULATOR_WEAPON_TYPES[int(v)]


class CalculatorWeapon(GenshinModel, Unique):
    """A weapon meant to be used with calculators"""

    id: int
    name: str
    icon: str
    rarity: int = Field(galias="weapon_level")
    type: str = Field(galias="weapon_cat_id")
    level: int = Field(0, galias="level_current")
    max_level: int

    @validator("type", pre=True)
    def __parse_weapon_type(cls, v: Any) -> str:
        if isinstance(v, str):
            return v

        return CALCULATOR_WEAPON_TYPES[int(v)]


class CalculatorArtifact(GenshinModel, Unique):
    """An artifact meant to be used with calculators"""

    id: int
    name: str
    icon: str
    rarity: int = Field(galias="reliquary_level")
    pos: int = Field(galias="reliquary_cat_id")
    level: int = Field(0, galias="level_current")
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
    level: int = Field(0, galias="level_current")
    max_level: int

    @property
    def type(self) -> Literal["attack", "skill", "burst", "passive", "dash"]:
        """The type of the talent, parsed from the group id"""
        # It's Possible to parse this from the id too but group id feels more reliable

        # 4139 -> group=41 identifier=3 order=9
        group, relevant = divmod(self.group_id, 100)
        identifier, order = divmod(relevant, 10)

        if identifier == 2:
            return "passive"
        elif order == 1:
            return "attack"
        elif order == 2:
            return "skill"
        elif order == 9:
            return "burst"
        elif order == 3:
            return "dash"
        else:
            raise ValueError(f"Cannot parse type for talent {self.group_id!r} (group {group})")

    @property
    def upgradeable(self) -> bool:
        """Whether this talent can be leveled up"""
        return self.type not in ("passive", "dash")

    def __int__(self) -> int:
        return self.group_id


class CalculatorConsumable(GenshinModel, Unique):
    """An item consumed when upgrading"""

    id: int
    name: str
    icon: str
    amount: int = Field(galias="num")


class CalculatorCharacterDetails(GenshinModel):
    """Details of a synced calculator character"""

    weapon: CalculatorWeapon = Field(galias="weapon")
    talents: List[CalculatorTalent] = Field(galias="skill_list")
    artifacts: List[CalculatorArtifact] = Field(galias="reliquary_list")

    @validator("talents")
    def __correct_talent_current_level(cls, v: List[CalculatorTalent]) -> List[CalculatorTalent]:
        # passive talent have current levels at 0 for some reason
        talents: List[CalculatorTalent] = []

        for talent in v:
            if talent.max_level == 1 and talent.level == 0:
                raw = talent.dict()
                raw["level"] = 1
                talent = CalculatorTalent(**raw)

            talents.append(talent)

        return v


class CalculatorArtifactResult(GenshinModel):
    """A calulation result for a specific artifact"""

    artifact_id: int = Field(galias="reliquary_id")
    list: List[CalculatorConsumable] = Field(galias="id_consume_list")


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

    id: Union[int, Unique]
    current: int
    target: int

    def _serialize(self, prefix: str = "") -> Dict[str, int]:
        """Serialize the object to a dict"""
        return {
            prefix + "id": int(self.id),
            prefix + "level_current": int(self.current),
            prefix + "level_target": int(self.target),
        }
