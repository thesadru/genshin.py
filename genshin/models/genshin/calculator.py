"""Genshin calculator models."""

from __future__ import annotations

import collections
import typing

import pydantic

from genshin.models.model import APIModel

from . import character

__all__ = [
    "CALCULATOR_ARTIFACTS",
    "CALCULATOR_ELEMENTS",
    "CALCULATOR_WEAPON_TYPES",
    "CalculatorArtifact",
    "CalculatorArtifactResult",
    "CalculatorCharacter",
    "CalculatorCharacterDetails",
    "CalculatorConsumable",
    "CalculatorFurnishing",
    "CalculatorFurnishingResults",
    "CalculatorResult",
    "CalculatorTalent",
    "CalculatorWeapon",
]

CALCULATOR_ELEMENTS: typing.Mapping[int, str] = {
    1: "Pyro",
    2: "Anemo",
    3: "Geo",
    4: "Dendro",
    5: "Electro",
    6: "Hydro",
    7: "Cryo",
}
CALCULATOR_WEAPON_TYPES: typing.Mapping[int, str] = {
    1: "Sword",
    10: "Catalyst",
    11: "Claymore",
    12: "Bow",
    13: "Polearm",
}
CALCULATOR_ARTIFACTS: typing.Mapping[int, str] = {
    1: "Flower of Life",
    2: "Plume of Death",
    3: "Sands of Eon",
    4: "Goblet of Eonothem",
    5: "Circlet of Logos",
}


class CalculatorCharacter(character.BaseCharacter):
    """Character meant to be used with calculators."""

    rarity: int = pydantic.Field(alias="avatar_level")
    element: str = pydantic.Field(alias="element_attr_id")
    weapon_type: str = pydantic.Field(alias="weapon_cat_id")
    level: int = pydantic.Field(alias="level_current", default=0)
    max_level: int

    @pydantic.field_validator("element", mode="before")
    @classmethod
    def __parse_element(cls, v: typing.Any) -> str:
        if isinstance(v, str):
            return v

        return CALCULATOR_ELEMENTS[int(v)]

    @pydantic.field_validator("weapon_type", mode="before")
    @classmethod
    def __parse_weapon_type(cls, v: typing.Any) -> str:
        if isinstance(v, str):
            return v

        return CALCULATOR_WEAPON_TYPES[int(v)]


class CalculatorWeapon(APIModel):
    """Weapon meant to be used with calculators."""

    id: int
    name: str
    icon: str
    rarity: int = pydantic.Field(alias="weapon_level")
    type: str = pydantic.Field(alias="weapon_cat_id")
    level: int = pydantic.Field(alias="level_current", default=0)
    max_level: int

    @pydantic.field_validator("type", mode="before")
    @classmethod
    def __parse_weapon_type(cls, v: typing.Any) -> str:
        if isinstance(v, str):
            return v

        return CALCULATOR_WEAPON_TYPES[int(v)]


class CalculatorArtifact(APIModel):
    """Artifact meant to be used with calculators."""

    id: int
    name: str
    icon: str
    rarity: int = pydantic.Field(alias="reliquary_level")
    pos: int = pydantic.Field(alias="reliquary_cat_id")
    level: int = pydantic.Field(alias="level_current", default=0)
    max_level: int

    @property
    def pos_name(self) -> str:
        return CALCULATOR_ARTIFACTS[self.pos]


class CalculatorTalent(APIModel):
    """Talent of a character meant to be used with calculators."""

    id: int
    group_id: int  # proudSkillGroupId
    name: str
    icon: str
    level: int = pydantic.Field(alias="level_current", default=0)
    max_level: int

    @property
    def type(self) -> typing.Literal["attack", "skill", "burst", "passive", "dash"] | None:
        """The type of the talent, parsed from the group id.

        Does not work for traveler!
        """
        # special cases
        if self.id == self.group_id:
            return "passive"  # maybe hoyo does this for unapgradables?

        if len(str(self.id)) == 6:  # in candSkillDepotIds
            return "attack"

        # 4139 -> group=41 identifier=3 order=9
        _, relevant = divmod(self.group_id, 100)
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
            return None

    @property
    def upgradeable(self) -> bool:
        """Whether this talent can be leveled up."""
        return self.type not in ("passive", "dash")

    def __int__(self) -> int:
        return self.group_id


class CalculatorFurnishing(APIModel):
    """Furnishing meant to be used with calculators."""

    id: int
    name: str
    icon: str = pydantic.Field(alias="icon_url")
    rarity: int = pydantic.Field(alias="level")

    amount: typing.Optional[int] = pydantic.Field(alias="num")


class CalculatorCharacterDetails(APIModel):
    """Details of a synced calculator character."""

    weapon: CalculatorWeapon = pydantic.Field(alias="weapon")
    talents: typing.Sequence[CalculatorTalent] = pydantic.Field(alias="skill_list")
    artifacts: typing.Sequence[CalculatorArtifact] = pydantic.Field(alias="reliquary_list")

    @pydantic.field_validator("talents")
    @classmethod
    def __correct_talent_current_level(cls, v: typing.Sequence[CalculatorTalent]) -> typing.Sequence[CalculatorTalent]:
        # passive talent have current levels at 0 for some reason
        talents: typing.List[CalculatorTalent] = []

        for talent in v:
            if talent.max_level == 1 and talent.level == 0:
                raw = talent.model_dump()
                raw["level"] = 1
                talent = CalculatorTalent(**raw)

            talents.append(talent)

        return v

    @property
    def upgradeable_talents(self) -> typing.Sequence[CalculatorTalent]:
        """All talents that can be leveled up."""
        if self.talents[2].type == "dash":
            return (self.talents[0], self.talents[1], self.talents[3])
        else:
            return (self.talents[0], self.talents[1], self.talents[2])


class CalculatorConsumable(APIModel):
    """Item consumed when upgrading."""

    id: int
    name: str
    icon: str
    amount: int = pydantic.Field(alias="num")


class CalculatorArtifactResult(APIModel):
    """Calculation result for a specific artifact."""

    artifact_id: int = pydantic.Field(alias="reliquary_id")
    list: typing.Sequence[CalculatorConsumable] = pydantic.Field(alias="id_consume_list")


class CalculatorResult(APIModel):
    """Calculation result."""

    character: typing.List[CalculatorConsumable] = pydantic.Field(alias="avatar_consume")
    weapon: typing.List[CalculatorConsumable] = pydantic.Field(alias="weapon_consume")
    talents: typing.List[CalculatorConsumable] = pydantic.Field(alias="avatar_skill_consume")
    artifacts: typing.List[CalculatorArtifactResult] = pydantic.Field(alias="reliquary_consume")

    @property
    def total(self) -> typing.Sequence[CalculatorConsumable]:
        artifacts = [i for a in self.artifacts for i in a.list]
        combined = self.character + self.weapon + self.talents + artifacts

        grouped: typing.Dict[int, typing.List[CalculatorConsumable]] = collections.defaultdict(list)
        for i in combined:
            grouped[i.id].append(i)

        total = [
            CalculatorConsumable(
                id=x[0].id,
                name=x[0].name,
                icon=x[0].icon,
                num=sum(i.amount for i in x),
            )
            for x in grouped.values()
        ]

        return total


class CalculatorFurnishingResults(APIModel):
    """Furnishing calculation result."""

    furnishings: typing.List[CalculatorConsumable] = pydantic.Field(alias="list")

    @property
    def total(self) -> typing.Sequence[CalculatorConsumable]:
        return self.furnishings
