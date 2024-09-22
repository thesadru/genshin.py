"""Calculator builder object.

Over-engineered for the sake of extendability and maintainability.
"""

from __future__ import annotations

import abc
import asyncio
import typing

import genshin.models.genshin as genshin_models
from genshin import types
from genshin.models.genshin import calculator as models

if typing.TYPE_CHECKING:
    from .client import CalculatorClient as Client

__all__ = ["Calculator", "FurnishingCalculator"]

T = typing.TypeVar("T")
CallableT = typing.TypeVar("CallableT", bound="typing.Callable[..., typing.Awaitable[object]]")


def _cache(func: CallableT) -> CallableT:
    """Cache a method."""

    async def wrapper(self: CalculatorState, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        async with self.lock:
            if value := self.cache.get(func.__name__):
                return value

            value = await func(self, *args, **kwargs)
            self.cache[func.__name__] = value

        return value

    return typing.cast("CallableT", wrapper)


class CalculatorState:
    """Stores character details if multiple objects require them."""

    client: Client
    cache: dict[str, typing.Any]
    lock: asyncio.Lock

    character_id: typing.Optional[int] = None

    def __init__(self, client: Client) -> None:
        self.client = client
        self.cache = {}
        self.lock = asyncio.Lock()

    @_cache
    async def get_character_details(self) -> models.CalculatorCharacterDetails:
        """Get character details."""
        if self.character_id is None:
            raise TypeError("No specified character.")

        return await self.client.get_character_details(self.character_id)

    @_cache
    async def get_character_talents(self) -> typing.Sequence[models.CalculatorTalent]:
        """Get talent ids."""
        if self.character_id is None:
            raise TypeError("No specified character.")

        return await self.client.get_character_talents(self.character_id)

    @_cache
    async def get_artifact_ids(self, artifact_id: int) -> typing.Sequence[int]:
        """Get artifact ids."""
        others = await self.client.get_complete_artifact_set(artifact_id)
        return [artifact_id] + [other.id for other in others]


class CalculatorResolver(abc.ABC, typing.Generic[T]):
    """Auto-resolving calculator object."""

    @abc.abstractmethod
    async def __call__(self, state: CalculatorState) -> T:
        """Resolve the object into concrete data."""


class CharacterResolver(CalculatorResolver[typing.Mapping[str, typing.Any]]):
    def __init__(
        self,
        character: types.IDOr[genshin_models.BaseCharacter],
        current: typing.Optional[int] = None,
        target: typing.Optional[int] = None,
        *,
        element: typing.Optional[int] = None,
    ) -> None:
        if isinstance(character, genshin_models.BaseCharacter):
            current = current or getattr(character, "level", None)
            character = character.id

        self.id = character
        self.current = current
        self.target = target
        self.element = element

    async def __call__(self, state: CalculatorState) -> typing.Mapping[str, typing.Any]:
        if self.current is None or self.target is None:
            return {}

        data = dict(
            avatar_id=self.id,
            avatar_level_current=self.current,
            avatar_level_target=self.target,
        )
        if self.element:
            data.update(element_attr_id=self.element)

        return data


class WeaponResolver(CalculatorResolver[typing.Mapping[str, typing.Any]]):
    id: int
    current: int
    target: int

    def __init__(self, weapon: int, current: int, target: int) -> None:
        self.id = weapon
        self.current = current
        self.target = target

    async def __call__(self, state: CalculatorState) -> typing.Mapping[str, typing.Any]:
        return dict(
            id=self.id,
            level_current=self.current,
            level_target=self.target,
        )


class CurrentWeaponResolver(WeaponResolver):
    id: int
    current: int
    target: int

    def __init__(self, target: int):
        self.target = target

    async def __call__(self, state: CalculatorState) -> typing.Mapping[str, typing.Any]:
        details = await state.get_character_details()
        self.id = details.weapon.id
        self.current = details.weapon.level
        return await super().__call__(state)


class ArtifactResolver(CalculatorResolver[typing.Sequence[typing.Mapping[str, typing.Any]]]):
    data: list[typing.Mapping[str, typing.Any]]

    def __init__(self) -> None:
        self.data = []

    def add_artifact(self, id: int, current: int, target: int) -> None:
        self.data.append(dict(id=id, level_current=current, level_target=target))

    async def __call__(self, state: CalculatorState) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
        return self.data


class ArtifactSetResolver(ArtifactResolver):
    def __init__(self, any_artifact_id: int, current: int, target: int) -> None:
        self.id = any_artifact_id
        self.current = current
        self.target = target

        super().__init__()

    async def __call__(self, state: CalculatorState) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
        artifact_ids = await state.get_artifact_ids(self.id)

        for artifact_id in artifact_ids:
            self.add_artifact(artifact_id, self.current, self.target)

        return self.data


class CurrentArtifactResolver(ArtifactResolver):
    artifacts: typing.Sequence[typing.Optional[int]]

    def __init__(
        self,
        target: typing.Optional[int] = None,
        *,
        flower: typing.Optional[int] = None,
        feather: typing.Optional[int] = None,
        sands: typing.Optional[int] = None,
        goblet: typing.Optional[int] = None,
        circlet: typing.Optional[int] = None,
    ) -> None:
        if target:
            self.artifacts = (target,) * 5
        else:
            self.artifacts = (flower, feather, sands, goblet, circlet)

    async def __call__(self, state: CalculatorState) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
        details = await state.get_character_details()

        for artifact in details.artifacts:
            if target := self.artifacts[artifact.pos - 1]:
                self.add_artifact(artifact.id, artifact.level, target)

        return self.data


class TalentResolver(CalculatorResolver[typing.Sequence[typing.Mapping[str, typing.Any]]]):
    data: list[typing.Mapping[str, typing.Any]]

    def __init__(self) -> None:
        self.data = []

    def add_talent(self, id: int, current: int, target: int) -> None:
        self.data.append(dict(id=id, level_current=current, level_target=target))

    async def __call__(self, state: CalculatorState) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
        return self.data


class CurrentTalentResolver(TalentResolver):
    talents: typing.Mapping[str, typing.Optional[int]]

    def __init__(
        self,
        target: typing.Optional[int] = None,
        current: typing.Optional[int] = None,
        *,
        attack: typing.Optional[int] = None,
        skill: typing.Optional[int] = None,
        burst: typing.Optional[int] = None,
    ) -> None:
        self.current = current
        if target:
            self.talents = {
                "attack": target,
                "skill": target,
                "burst": target,
            }
        else:
            self.talents = {
                "attack": attack,
                "skill": skill,
                "burst": burst,
            }

        super().__init__()

    async def __call__(self, state: CalculatorState) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
        if self.current:
            talents = await state.get_character_talents()
        else:
            details = await state.get_character_details()
            talents = details.talents
            self.current = 0

        if talents[2].type == "dash":
            ordered = (talents[0], talents[1], talents[3])
        else:
            ordered = (talents[0], talents[1], talents[2])

        for talent, name in zip(ordered, ("attack", "skill", "burst")):
            if target := self.talents[name]:
                self.add_talent(talent.group_id, talent.level or self.current, target)

        return self.data


class Calculator:
    """Builder for the genshin impact enhancement calculator."""

    client: Client
    lang: typing.Optional[str]

    character: typing.Optional[CharacterResolver]
    weapon: typing.Optional[WeaponResolver]
    artifacts: typing.Optional[ArtifactResolver]
    talents: typing.Optional[TalentResolver]

    _state: CalculatorState

    def __init__(self, client: Client, *, lang: typing.Optional[str] = None) -> None:
        self.client = client
        self.lang = lang

        self.character = None
        self.weapon = None
        self.artifacts = None
        self.talents = None

        self._state = CalculatorState(client)

    def set_character(
        self,
        character: types.IDOr[genshin_models.BaseCharacter],
        current: typing.Optional[int] = None,
        target: typing.Optional[int] = None,
        *,
        element: typing.Optional[int] = None,
    ) -> Calculator:
        """Set the character."""
        self.character = CharacterResolver(character, current, target, element=element)
        self._state.character_id = self.character.id
        return self

    def set_weapon(self, id: int, current: int, target: int) -> Calculator:
        """Set the weapon."""
        self.weapon = WeaponResolver(id, current, target)
        return self

    def add_artifact(self, id: int, current: int, target: int) -> Calculator:
        """Add an artifact."""
        if type(self.artifacts) is not ArtifactResolver:
            self.artifacts = ArtifactResolver()

        self.artifacts.add_artifact(id, current, target)
        return self

    def set_artifact_set(self, any_artifact_id: int, current: int, target: int) -> Calculator:
        """Set an artifact set."""
        self.artifacts = ArtifactSetResolver(any_artifact_id, current, target)
        return self

    def add_talent(self, group_id: int, current: int, target: int) -> Calculator:
        """Add a talent."""
        if type(self.talents) is not TalentResolver:
            self.talents = TalentResolver()

        self.talents.add_talent(group_id, current, target)
        return self

    def with_current_weapon(self, target: int) -> Calculator:
        """Set the weapon of the selected character."""
        self.weapon = CurrentWeaponResolver(target)
        return self

    def with_current_artifacts(
        self,
        target: typing.Optional[int] = None,
        *,
        flower: typing.Optional[int] = None,
        feather: typing.Optional[int] = None,
        sands: typing.Optional[int] = None,
        goblet: typing.Optional[int] = None,
        circlet: typing.Optional[int] = None,
    ) -> Calculator:
        """Add all artifacts of the selected character."""
        self.artifacts = CurrentArtifactResolver(
            target,
            flower=flower,
            feather=feather,
            sands=sands,
            goblet=goblet,
            circlet=circlet,
        )
        return self

    def with_current_talents(
        self,
        target: typing.Optional[int] = None,
        current: typing.Optional[int] = None,
        *,
        attack: typing.Optional[int] = None,
        skill: typing.Optional[int] = None,
        burst: typing.Optional[int] = None,
    ) -> Calculator:
        """Add all talents of the currently selected character."""
        self.talents = CurrentTalentResolver(
            target=target,
            current=current,
            attack=attack,
            skill=skill,
            burst=burst,
        )
        return self

    async def build(self) -> typing.Mapping[str, typing.Any]:
        """Build the calculator object."""
        data: dict[str, typing.Any] = {}

        if self.character:
            data.update(await self.character(self._state))

        if self.weapon:
            data["weapon"] = await self.weapon(self._state)

        if self.artifacts:
            data["reliquary_list"] = await self.artifacts(self._state)

        if self.talents:
            data["skill_list"] = await self.talents(self._state)

        return data

    async def calculate(self) -> models.CalculatorResult:
        """Execute the calculator."""
        return await self.client._execute_calculator(await self.build(), lang=self.lang)

    def __await__(self) -> typing.Generator[typing.Any, None, models.CalculatorResult]:
        return self.calculate().__await__()


class FurnishingCalculator:
    """Builder for the genshin impact furnishing calculator."""

    client: Client
    lang: typing.Optional[str]

    furnishings: dict[int, int]
    replica_code: typing.Optional[int] = None
    replica_region: typing.Optional[str] = None

    def __init__(self, client: Client, *, lang: typing.Optional[str] = None) -> None:
        self.client = client
        self.lang = lang

        self.furnishings = {}
        self.replica_code = None
        self.replica_region = None

    def add_furnishing(self, id: types.IDOr[models.CalculatorFurnishing], amount: int = 1) -> FurnishingCalculator:
        """Add a furnishing."""
        self.furnishings.setdefault(int(id), 0)
        self.furnishings[int(id)] += amount
        return self

    def with_replica(self, code: int, *, region: typing.Optional[str] = None) -> FurnishingCalculator:
        """Set the replica code."""
        self.replica_code = code
        self.replica_region = region
        return self

    async def build(self) -> typing.Mapping[str, typing.Any]:
        """Build the calculator object."""
        data: dict[str, typing.Any] = {}

        if self.replica_code:
            furnishings = await self.client.get_teapot_replica_blueprint(self.replica_code, region=self.replica_region)
            self.furnishings.update({furnishing.id: furnishing.amount or 1 for furnishing in furnishings})

        data["list"] = [{"id": id, "cnt": amount} for id, amount in self.furnishings.items()]

        return data

    async def calculate(self) -> models.CalculatorFurnishingResults:
        """Execute the calculator."""
        return await self.client._execute_furnishings_calculator(await self.build(), lang=self.lang)

    def __await__(self) -> typing.Generator[typing.Any, None, models.CalculatorFurnishingResults]:
        return self.calculate().__await__()
