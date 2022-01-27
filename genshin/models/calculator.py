from __future__ import annotations

import collections
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Literal,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)

from pydantic import Field, validator

from .base import BaseCharacter, GenshinModel, Unique

if TYPE_CHECKING:
    from genshin import GenshinClient

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
    "CalculatorBuilder",
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

    id: int
    current: Optional[int]
    target: Optional[int]

    def _serialize(self, prefix: str = "") -> Dict[str, int]:
        """Serialize the object to a dict"""
        if self.id is None or self.current is None or self.target is None:
            raise ValueError("Cannot calculate with partial data")

        return {
            prefix + "id": int(self.id),
            prefix + "level_current": int(self.current),
            prefix + "level_target": int(self.target),
        }


class CalculatorBuilder:
    """A builder for the genshin impact enhancement calculator"""

    client: GenshinClient
    lang: Optional[str] = None

    character: Optional[CalculatorObject] = None
    weapon: Optional[CalculatorObject] = None
    artifacts: List[CalculatorObject]
    talents: List[CalculatorObject]

    character_element: Optional[int] = None
    full_artifact_set: bool = False
    include_talents_current_level: Optional[int] = None
    include_weapon: Optional[int] = None
    include_artifacts: Optional[Tuple[Optional[int], ...]] = None
    include_talents: Optional[Dict[str, Optional[int]]] = None

    def __init__(self, client: GenshinClient, lang: str = None) -> None:
        self.client = client
        self.lang = lang
        self.artifacts = []
        self.talents = []

    def set_lang(self, lang: str):
        """Set the language"""
        self.lang = lang

        return self

    def set_character(
        self,
        character: Union[int, BaseCharacter],
        current: int = None,
        target: int = None,
        *,
        element: int = None,
    ):
        """Set the character"""
        if isinstance(character, int):
            id = character
        else:
            id = character.id
            current = current or getattr(character, "level")

        self.character = CalculatorObject(id, current, target)
        self.character_element = element

        return self

    def set_weapon(self, id: int, current: int, target: int):
        """Set the weapon"""
        self.weapon = CalculatorObject(id, current, target)

        return self

    def add_artifact(self, id: int, current: int, target: int, *, full_set: bool = False):
        """Add an artifact"""
        self.artifacts.append(CalculatorObject(id, current, target))
        self.full_artifact_set = full_set

        return self

    def set_artifact_set(self, any_artifact_id: int, current: int, target: int):
        """Add an artifact set"""
        self.artifacts.append(CalculatorObject(any_artifact_id, current, target))
        self.full_artifact_set = True

        return self

    def add_talent(self, group_id: int, current: int, target: int):
        """Add a talent"""
        self.talents.append(CalculatorObject(group_id, current, target))

        return self

    def with_current_weapon(self, target: int):
        self.include_weapon = target

        return self

    def with_current_artifacts(
        self,
        target: int = None,
        *,
        flower: int = None,
        feather: int = None,
        sands: int = None,
        goblet: int = None,
        circlet: int = None,
    ):
        """Add all artifacts of the selected character"""
        if target:
            self.include_artifacts = (target,) * 5
        else:
            self.include_artifacts = (flower, feather, sands, goblet, circlet)

        return self

    def with_current_talents(
        self,
        target: int = None,
        current: int = None,
        *,
        attack: int = None,
        skill: int = None,
        burst: int = None,
    ):
        """Add all talents of the currently selected character"""
        if target:
            self.include_talents = {
                "attack": target,
                "skill": target,
                "burst": target,
            }
        else:
            self.include_talents = {
                "attack": attack,
                "skill": skill,
                "burst": burst,
            }

        self.include_talents_current_level = current

        return self

    async def build(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        details: Optional[CalculatorCharacterDetails] = None

        if self.character_element:
            data["element_attr_id"] = self.character_element

        if self.character:
            data.update(self.character._serialize(prefix="avatar_"))

        if self.weapon:
            data["weapon"] = self.weapon._serialize()

        if self.artifacts:
            if self.full_artifact_set:
                if len(self.artifacts) != 1:
                    raise TypeError("Must have exactly 1 artifact to make a full set")

                original = self.artifacts[0]
                rest = await self.client.get_complete_artifact_set(original.id)
                self.artifacts += [
                    CalculatorObject(a.id, original.current, original.target) for a in rest
                ]

            data["reliquary_list"] = [i._serialize() for i in self.artifacts]

        if self.talents:
            data["skill_list"] = [i._serialize() for i in self.talents]

        if self.include_weapon:
            if self.character is None:
                raise TypeError("No character to get a weapon from")

            details = details or await self.client.get_character_details(self.character.id)

            x = CalculatorObject(details.weapon.id, details.weapon.level, self.include_weapon)
            data["weapon"] = x._serialize()

        if self.include_artifacts:
            if self.character is None:
                raise TypeError("No character to get artifacts from")

            details = details or await self.client.get_character_details(self.character.id)

            data["reliquary_list"] = []
            for artifact in details.artifacts:
                if target := self.include_artifacts[artifact.pos - 1]:
                    x = CalculatorObject(artifact.id, artifact.level, target)
                    data["reliquary_list"].append(x._serialize())

        if self.include_talents:
            if self.character is None:
                raise TypeError("No character to get talents from")

            current = self.include_talents_current_level or 0
            if current:
                talents = await self.client.get_character_talents(self.character.id)
            else:
                details = details or await self.client.get_character_details(self.character.id)
                talents = details.talents

            data["skill_list"] = []
            for talent in talents:
                if target := self.include_talents.get(talent.type):
                    x = CalculatorObject(talent.group_id, talent.level or current, target)
                    data["skill_list"].append(x._serialize())

        return data

    async def calculate(self) -> CalculatorResult:
        return await self.client._execute_calculator(self)

    def __await__(self) -> Generator[Any, None, CalculatorResult]:
        return self.calculate().__await__()
