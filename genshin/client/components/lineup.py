"""Lineup component."""

import functools
import typing

import genshin.models.genshin as genshin_models
from genshin import paginators, types, utility
from genshin.client import cache, routes
from genshin.client.components import base
from genshin.client.manager import managers
from genshin.models.genshin import lineup as models

__all__ = ["LineupClient"]


class LineupClient(base.BaseClient):
    """Lineup component."""

    async def request_lineup(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the lineup endpoint."""
        params = dict(params or {})

        base_url = routes.LINEUP_URL.get_url(self.region)
        url = base_url / endpoint

        params["lang"] = lang or self.lang

        return await self.request(url, method=method, params=params, **kwargs)

    async def get_lineup_fields(
        self, *, lang: typing.Optional[str] = None, use_cache: bool = True
    ) -> models.LineupFields:
        """Get configuration lineup fields."""
        data = await self.request_lineup(
            "config",
            lang=lang,
            static_cache=cache.cache_key("lineup", endpoint="config", lang=lang or self.lang) if use_cache else None,
        )

        return models.LineupFields(**data)

    async def get_lineup_scenarios(
        self,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.LineupScenarios:
        """Get lineup scenarios."""
        data = await self.request_lineup(
            "tags",
            lang=lang,
            static_cache=cache.cache_key("lineup", endpoint="tags", lang=lang or self.lang),
        )
        dummy: dict[str, typing.Any] = dict(id=0, name="", children=data["tree"])

        return models.LineupScenarios(**dummy)

    async def _get_lineup_page(
        self,
        token: str,
        *,
        limit: typing.Optional[int] = None,
        tag_id: typing.Optional[int] = None,
        roles: typing.Optional[typing.Sequence[int]] = None,
        order: typing.Optional[str] = None,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> tuple[str, typing.Sequence[models.LineupPreview]]:
        """Get a single page of lineups."""
        params: dict[str, typing.Any] = dict(
            next_page_token=token,
            limit=limit or "",
            tag_id=tag_id or "",
            order=order or "",
            roles=roles or "",
        )

        if order == "Match":
            uid = uid or await self._get_uid(types.Game.GENSHIN)

            params["uid"] = uid
            params["region"] = utility.recognize_genshin_server(uid)

        data = await self.request_lineup("lineup/index", lang=lang, params=params)

        return data["next_page_token"], [models.LineupPreview(**i) for i in data["list"]]

    def get_lineups(
        self,
        scenario: typing.Optional[types.IDOr[models.LineupScenario]] = None,
        *,
        limit: typing.Optional[int] = None,
        page_size: typing.Optional[int] = None,
        newest: bool = False,
        match_characters: bool = False,
        characters: typing.Optional[typing.Sequence[types.IDOr[genshin_models.Character]]] = None,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> paginators.TokenPaginator[models.LineupPreview]:
        """Get lineups."""
        if scenario is not None:
            scenario = int(scenario)

        character_ids = [int(i) for i in characters] if characters is not None else None

        if match_characters:
            order = "Match"
        else:
            order = "CreatedTime" if newest else "Hot"

        return paginators.TokenPaginator(
            functools.partial(
                self._get_lineup_page,
                tag_id=scenario,
                roles=character_ids,
                order=order,
                uid=uid,
                lang=lang,
            ),
            limit=limit,
            page_size=page_size,
        )

    async def get_lineup_details(
        self,
        lineup: typing.Union[str, models.LineupPreview],
        *,
        lang: typing.Optional[str] = None,
    ) -> models.Lineup:
        """Get lineup with detailed characters."""
        lineup_id = lineup if isinstance(lineup, str) else lineup.id

        data = await self.request_lineup(
            "lineup/detail",
            lang=lang,
            params=dict(id=lineup_id),
            cache=cache.cache_key("lineup", endpoint="detail", id=lineup_id, lang=lang or self.lang),
        )

        return models.Lineup(**data["lineup"])

    @managers.no_multi
    async def get_user_lineups(
        self,
        *,
        limit: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.LineupPreview]:
        """Get lineups of the currently logged-in user."""
        data = await self.request_lineup(
            "user/lineup",
            lang=lang,
            params=dict(limit=limit or 1000),
            cache=cache.cache_key("lineup", endpoint="user", lang=lang or self.lang),
        )

        return [models.LineupPreview(**i) for i in data["list"]]

    @managers.no_multi
    async def get_favorite_lineups(
        self,
        *,
        limit: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.LineupPreview]:
        """Get favorited lineups of the currently logged-in user."""
        data = await self.request_lineup(
            "user/favour_lineup",
            lang=lang,
            params=dict(limit=limit or 1000),
            cache=cache.cache_key("lineup", endpoint="favorite", lang=lang or self.lang),
        )

        return [models.LineupPreview(**i) for i in data["list"]]

    @managers.no_multi
    async def get_lineup_character_history(
        self,
        *,
        limit: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.LineupCharacter]:
        """Get previous character builds of the currently logged-in user.."""
        data = await self.request_lineup(
            "lineup/history",
            lang=lang,
            params=dict(limit=limit or 1000),
            cache=cache.cache_key("lineup", endpoint="history", lang=lang or self.lang),
        )

        return [models.LineupCharacter(**i) for i in data["list"]]
