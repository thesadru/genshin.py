"""Lineup component."""
import typing

from genshin import types, utility
from genshin.client import cache, routes
from genshin.client.components import base
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

    async def get_lineup_fields(self, *, lang: typing.Optional[str] = None) -> models.LineupFields:
        """Get configuration lineup fields."""
        data = await self.request_lineup(
            "config",
            lang=lang,
            static_cache=cache.cache_key("lineup", endpoint="config", lang=lang or self.lang),
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
        dummy: typing.Dict[str, typing.Any] = dict(id=0, name="", children=data["tree"])

        return models.LineupScenarios(**dummy)

    async def _get_lineup_page(
        self,
        token: str,
        *,
        tag_id: int,
        roles: typing.Sequence[int],
        order: str,
        lang: typing.Optional[str] = None,
        uid: typing.Optional[int] = None,
    ) -> typing.Tuple[str, typing.Sequence[models.LineupPreview]]:
        """Get a single page of lineups."""
        params: typing.Dict[str, typing.Any] = dict(
            next_page_token=token,
            tag_id=tag_id,
            order=order,
            roles=roles,
        )

        if order == "Match":
            uid = uid or await self._get_uid(types.Game.GENSHIN)

            params["uid"] = uid
            params["region"] = utility.recognize_genshin_server(uid)

        data = await self.request_lineup("lineup/index", lang=lang, params=params)

        return data["next_page_token"], [models.LineupPreview(**i) for i in data["list"]]
