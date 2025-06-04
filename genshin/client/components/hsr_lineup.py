import typing

import aiohttp.typedefs
from genshin import types
from genshin.client import routes
from genshin.client.components import base
from genshin.constants import GAME_LANGS
from genshin.utility import ds
from genshin.models.starrail import rpgsimulator as models


class HSRLineupClient(base.BaseClient):
    """HSR lineup simulator client."""

    async def _request(
        self,
        endpoint: str,
        *,
        lang: typing.Optional[str] = None,
        region: typing.Optional[types.Region] = None,
        method: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        data: typing.Any = None,
        headers: typing.Optional[aiohttp.typedefs.LooseHeaders] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request any hoyolab endpoint."""
        if lang is not None and lang not in GAME_LANGS[types.Game.STARRAIL]:
            raise ValueError(f"Invalid language {lang!r} for game {types.Game.STARRAIL}.")

        lang = lang or self.lang
        region = region or self.region

        url = routes.HSR_LINEUP_SIMULATOR_URL.get_url() / endpoint

        headers = base.parse_loose_headers(headers)
        headers.update(ds.get_ds_headers(data=data, params=params, region=region, lang=lang))

        return await self.request(url, method=method, params=params, data=data, headers=headers, **kwargs)

    async def get_hsr_lineup_game_modes(self, *, lang: typing.Optional[str] = None) -> list[models.HSRGameMode]:
        """Get the available game modes for the HSR lineup simulator."""
        data = await self._request("tag", lang=lang)
        return [models.HSRGameMode(**item) for item in data["tree"]]
