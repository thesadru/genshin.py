"""Calculator client."""

from __future__ import annotations

import asyncio
import logging
import typing
import warnings

import aiohttp.typedefs

import genshin.models.genshin as genshin_models
from genshin import errors, types, utility
from genshin.client import cache as client_cache
from genshin.client import routes
from genshin.client.components import base
from genshin.models.genshin import calculator as models
from genshin.utility import deprecation

from .calculator import Calculator, FurnishingCalculator

__all__ = ["CalculatorClient"]


_LOGGER = logging.getLogger(__name__)


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
        headers: typing.Optional[aiohttp.typedefs.LooseHeaders] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the calculator endpoint."""
        params = dict(params or {})
        headers = base.parse_loose_headers(headers)

        base_url = routes.CALCULATOR_URL.get_url(self.region)
        url = base_url / endpoint

        if method == "GET":
            params["lang"] = lang or self.lang
            data = None
        else:
            data = dict(data or {})
            data["lang"] = lang or self.lang

        if self.region == types.Region.CHINESE:
            headers["referer"] = str(routes.CALCULATOR_REFERER_URL.get_url())
        update_task = asyncio.create_task(utility.update_characters_any(lang or self.lang, lenient=True))

        data = await self.request(url, method=method, params=params, data=data, headers=headers, **kwargs)

        try:
            await update_task
        except Exception as e:
            warnings.warn(f"Failed to update characters: {e!r}")

        return data

    async def _execute_calculator(
        self,
        data: typing.Mapping[str, typing.Any],
        *,
        lang: typing.Optional[str] = None,
    ) -> models.CalculatorResult:
        """Calculate the results of a builder."""
        data = await self.request_calculator("compute", lang=lang, data=data)
        return models.CalculatorResult(**data)

    async def _execute_furnishings_calculator(
        self,
        data: typing.Mapping[str, typing.Any],
        *,
        lang: typing.Optional[str] = None,
    ) -> models.CalculatorFurnishingResults:
        """Calculate the results of a builder."""
        data = await self.request_calculator("furniture/compute", lang=lang, data=data)
        return models.CalculatorFurnishingResults(**data)

    def calculator(self, *, lang: typing.Optional[str] = None) -> Calculator:
        """Create a calculator builder object."""
        return Calculator(self, lang=lang)

    def furnishings_calculator(self, *, lang: typing.Optional[str] = None) -> FurnishingCalculator:
        """Create a calculator builder object."""
        return FurnishingCalculator(self, lang=lang)

    async def _enable_calculator_sync(self, enabled: bool = True) -> None:
        """Enable data syncing in calculator."""
        await self.request_calculator("avatar/auth", method="POST", data=dict(avatar_auth=int(enabled)))

    async def _get_calculator_items(
        self,
        slug: str,
        filters: typing.Mapping[str, typing.Any],
        query: typing.Optional[str] = None,
        *,
        uid: typing.Optional[int] = None,
        is_all: bool = False,
        sync: bool = False,
        lang: typing.Optional[str] = None,
        autoauth: bool = True,
    ) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
        """Get all items of a specific slug from a calculator."""
        endpoint = f"sync/{slug}/list" if sync else f"{slug}/list"

        if query:
            if any(filters.values()):
                raise TypeError("Cannot specify a query and filter at the same time")

            filters = dict(keywords=query, **filters)

        payload: dict[str, typing.Any] = dict(page=1, size=69420, is_all=is_all, **filters)

        if sync:
            uid = uid or await self._get_uid(types.Game.GENSHIN)
            payload["uid"] = uid
            payload["region"] = utility.recognize_genshin_server(uid)

        cache: typing.Optional[client_cache.CacheKey] = None
        if not any(filters.values()) and not sync:
            cache = client_cache.cache_key("calculator", slug=slug, lang=lang or self.lang)

        try:
            data = await self.request_calculator(endpoint, lang=lang, data=payload, cache=cache)
        except errors.GenshinException as e:
            if e.retcode != -502002:  # Sync not enabled
                raise
            if not autoauth:
                raise errors.GenshinException(e.response, "Calculator sync is not enabled") from e

            await self._enable_calculator_sync()
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
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.CalculatorCharacter]:
        """Get all characters provided by the Enhancement Progression Calculator."""
        data = await self._get_calculator_items(
            "avatar",
            lang=lang,
            is_all=include_traveler,
            sync=sync,
            uid=uid,
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

    async def get_calculator_furnishings(
        self,
        *,
        types: typing.Optional[int] = None,
        rarities: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.CalculatorFurnishing]:
        """Get all furnishings provided by the Enhancement Progression Calculator."""
        data = await self._get_calculator_items(
            "furniture",
            lang=lang,
            filters=dict(
                cat_id=types or 0,
                weapon_levels=rarities or 0,
            ),
        )
        return [models.CalculatorFurnishing(**i) for i in data]

    async def get_character_details(
        self,
        character: types.IDOr[genshin_models.BaseCharacter],
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> models.CalculatorCharacterDetails:
        """Get the weapon, artifacts and talents of a character.

        Not related to the Battle Chronicle.
        This data is always private.
        """
        uid = uid or await self._get_uid(types.Game.GENSHIN)

        data = await self.request_calculator(
            "sync/avatar/detail",
            method="GET",
            lang=lang,
            params=dict(
                avatar_id=int(character),
                uid=uid,
                region=utility.recognize_genshin_server(uid),
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

    async def get_teapot_replica_blueprint(
        self,
        share_code: int,
        *,
        region: typing.Optional[str] = None,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.CalculatorFurnishing]:
        """Get furnishings used by a teapot replica blueprint."""
        if not region:
            uid = uid or await self._get_uid(types.Game.GENSHIN)
            region = utility.recognize_genshin_server(uid)

        data = await self.request_calculator(
            "furniture/blueprint",
            method="GET",
            lang=lang,
            params=dict(share_code=share_code, region=region),
            cache=client_cache.cache_key("calculator", slug="blueprint", share_code=share_code, lang=lang or self.lang),
        )
        return [models.CalculatorFurnishing(**i) for i in data["list"]]

    @deprecation.deprecated("await genshin.utility.update_characters_any()")
    async def update_character_names(self, *, lang: typing.Optional[str] = None) -> None:
        """Update stored db characters with the names from the calculator."""
        characters = await self.get_calculator_characters(lang=lang, include_traveler=True)

        for char in characters:
            icon = genshin_models.character._parse_icon(char.icon)
            dbchar = genshin_models.DBChar(
                char.id, icon, char.name, "" if "Player" in icon else char.element, char.rarity
            )

            genshin_models.CHARACTER_NAMES[lang or self.lang][dbchar.id] = dbchar
