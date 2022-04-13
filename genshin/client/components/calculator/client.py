"""Calculator client."""
from __future__ import annotations

import typing

import genshin.models.genshin as genshin_models
from genshin import types
from genshin.client import cache as client_cache
from genshin.client import routes
from genshin.client.components import base
from genshin.models.genshin import calculator as models
from genshin.utility import genshin as genshin_utility

from .calculator import Calculator

__all__ = ["CalculatorClient"]


class CalculatorClient(base.BaseClient):
    """Calculator component."""

    async def request_calculator(
        self,
        endpoint: str,
        *,
        method: str = "POST",
        lang: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        data: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the calculator endpoint."""
        params = dict(params or {})

        base_url = routes.CALCULATOR_URL.get_url(self.region)
        url = base_url / endpoint

        if method == "GET":
            params["lang"] = lang or self.lang
            data = None
        else:
            data = dict(data or {})
            data["lang"] = lang or self.lang

        return await self.request(url, method=method, params=params, data=data, **kwargs)

    async def _execute_calculator(
        self,
        data: typing.Mapping[str, typing.Any],
        *,
        lang: typing.Optional[str] = None,
    ) -> models.CalculatorResult:
        """Calculate the results of a builder."""
        data = await self.request_calculator("compute", lang=lang, data=data)
        return models.CalculatorResult(**data)

    def calculator(self, *, lang: typing.Optional[str] = None) -> Calculator:
        """Create a calculator builder object."""
        return Calculator(self, lang=lang)

    async def _get_calculator_items(
        self,
        slug: str,
        filters: typing.Mapping[str, typing.Any],
        query: typing.Optional[str] = None,
        *,
        is_all: bool = False,
        sync: bool = False,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
        """Get all items of a specific slug from a calculator."""
        endpoint = f"sync/{slug}/list" if sync else f"{slug}/list"

        if query:
            if any(filters.values()):
                raise TypeError("Cannot specify a query and filter at the same time")

            filters = dict(keywords=query, **filters)

        payload: typing.Dict[str, typing.Any] = dict(page=1, size=69420, is_all=is_all, **filters)

        if sync:
            uid = await self._get_uid(types.Game.GENSHIN)
            payload["uid"] = uid
            payload["region"] = genshin_utility.recognize_genshin_server(uid)

        cache: typing.Optional[client_cache.CacheKey] = None
        if not any(filters.values()) and not sync:
            cache = client_cache.cache_key("calculator", slug=slug, lang=lang or self.lang)

        data = await self.request_calculator(endpoint, lang=lang, data=payload, cache=cache)
        return data["list"]

    async def get_calculator_characters(
        self,
        *,
        query: typing.Optional[str] = None,
        elements: typing.Optional[typing.Sequence[int]] = None,
        weapon_types: typing.Optional[typing.Sequence[int]] = None,
        include_traveler: bool = False,
        sync: bool = False,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.CalculatorCharacter]:
        """Get all characters provided by the Enhancement Progression Calculator."""
        data = await self._get_calculator_items(
            "avatar",
            lang=lang,
            is_all=include_traveler,
            sync=sync,
            query=query,
            filters=dict(
                element_attr_ids=elements or [],
                weapon_cat_ids=weapon_types or [],
            ),
        )
        return [models.CalculatorCharacter(**i) for i in data]

    async def get_calculator_weapons(
        self,
        *,
        query: typing.Optional[str] = None,
        types: typing.Optional[typing.Sequence[int]] = None,
        rarities: typing.Optional[typing.Sequence[int]] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.CalculatorWeapon]:
        """Get all weapons provided by the Enhancement Progression Calculator."""
        data = await self._get_calculator_items(
            "weapon",
            lang=lang,
            query=query,
            filters=dict(
                weapon_cat_ids=types or [],
                weapon_levels=rarities or [],
            ),
        )
        return [models.CalculatorWeapon(**i) for i in data]

    async def get_calculator_artifacts(
        self,
        *,
        query: typing.Optional[str] = None,
        pos: int = 1,
        rarities: typing.Optional[typing.Sequence[int]] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.CalculatorArtifact]:
        """Get all artifacts provided by the Enhancement Progression Calculator."""
        data = await self._get_calculator_items(
            "reliquary",
            lang=lang,
            query=query,
            filters=dict(
                reliquary_cat_id=pos,
                reliquary_levels=rarities or [],
            ),
        )
        return [models.CalculatorArtifact(**i) for i in data]

    async def get_character_details(
        self,
        character: types.IDOr[genshin_models.BaseCharacter],
        *,
        lang: typing.Optional[str] = None,
    ) -> models.CalculatorCharacterDetails:
        """Get the weapon, artifacts and talents of a character.

        Not related to the Battle Chronicle.
        This data is always private.
        """
        uid = await self._get_uid(types.Game.GENSHIN)

        data = await self.request_calculator(
            "sync/avatar/detail",
            method="GET",
            lang=lang,
            params=dict(
                avatar_id=int(character),
                uid=uid,
                region=genshin_utility.recognize_genshin_server(uid),
            ),
        )
        return models.CalculatorCharacterDetails(**data)

    async def get_character_talents(
        self,
        character: types.IDOr[genshin_models.BaseCharacter],
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.CalculatorTalent]:
        """Get the talents of a character.

        This only gets the talent names, not their levels.
        Use `get_character_details` for precise information.
        """
        data = await self.request_calculator(
            "avatar/skill_list",
            method="GET",
            lang=lang,
            params=dict(avatar_id=int(character)),
        )
        return [models.CalculatorTalent(**i) for i in data["list"]]

    async def get_complete_artifact_set(
        self,
        artifact: types.IDOr[typing.Union[genshin_models.Artifact, genshin_models.CalculatorArtifact]],
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.CalculatorArtifact]:
        """Get all other artifacts that share a set with any given artifact.

        Doesn't return the artifact passed into this function.
        """
        data = await self.request_calculator(
            "reliquary/set",
            method="GET",
            lang=lang,
            params=dict(reliquary_id=int(artifact)),
            cache=client_cache.cache_key("calculator", slug="set", artifact=int(artifact), lang=lang or self.lang),
        )
        return [models.CalculatorArtifact(**i) for i in data["reliquary_list"]]

    async def _get_all_artifact_ids(self, artifact_id: int) -> typing.Sequence[int]:
        """Get all artifact ids in the same set as a given artifact id."""
        others = await self.get_complete_artifact_set(artifact_id)
        return [artifact_id] + [other.id for other in others]
