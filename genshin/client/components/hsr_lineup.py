import typing

import aiohttp.typedefs

from genshin import types
from genshin.client import routes
from genshin.client.components import base
from genshin.constants import GAME_LANGS
from genshin.models.starrail import rpgsimulator as models
from genshin.utility import ds

__all__ = ("HSRLineupClient",)


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

    async def get_starrail_lineup_game_modes(
        self, *, lang: typing.Optional[str] = None
    ) -> list[models.StarRailGameMode]:
        """Get the available game modes for the HSR lineup simulator."""
        data = await self._request("tag", lang=lang)
        return [models.StarRailGameMode(**item) for item in data["tree"]]

    @typing.overload
    async def get_starrail_lineups(
        self,
        *,
        tag_id: int,
        group_id: int,
        type: typing.Literal["moc"],
        next_page_token: typing.Optional[str] = ...,
        lang: typing.Optional[str] = ...,
    ) -> models.StarRailLineupResponse: ...
    @typing.overload
    async def get_starrail_lineups(
        self,
        *,
        tag_id: int,
        group_id: int,
        type: typing.Literal["pf"],
        next_page_token: typing.Optional[str] = ...,
        lang: typing.Optional[str] = ...,
    ) -> models.PureFictionLineupResponse: ...
    @typing.overload
    async def get_starrail_lineups(
        self,
        *,
        tag_id: int,
        group_id: int,
        type: typing.Literal["apc"],
        next_page_token: typing.Optional[str] = ...,
        lang: typing.Optional[str] = ...,
    ) -> models.APCShadowLineupResponse: ...
    async def get_starrail_lineups(
        self,
        *,
        tag_id: int,
        group_id: int,
        type: typing.Literal["moc", "pf", "apc"],
        next_page_token: typing.Optional[str] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Union[models.StarRailLineupResponse, models.PureFictionLineupResponse, models.APCShadowLineupResponse]:
        """Get the available lineups for the HSR lineup simulator."""
        type_convert = {"moc": "Chasm", "pf": "Story", "apc": "Boss"}
        if type not in type_convert:
            msg = f"Invalid type {type!r} for HSR lineup."
            raise ValueError(msg)

        params: dict[str, typing.Any] = {
            "tag_id": tag_id,
            "group_id": group_id,
            "lineup_type": type_convert[type],
        }
        if next_page_token:
            params["page_token"] = next_page_token

        data = await self._request("lineup/index", lang=lang, params=params)

        if type == "pf":
            return models.PureFictionLineupResponse(**data)
        elif type == "apc":
            return models.APCShadowLineupResponse(**data)
        return models.StarRailLineupResponse(**data)

    @typing.overload
    async def get_starrail_lineup_schedules(
        self, type: typing.Literal["moc"], *, lang: typing.Optional[str] = ...
    ) -> list[models.MOCSchedule]: ...
    @typing.overload
    async def get_starrail_lineup_schedules(
        self, type: typing.Literal["pf"], *, lang: typing.Optional[str] = ...
    ) -> list[models.PureFictionSchedule]: ...
    @typing.overload
    async def get_starrail_lineup_schedules(
        self, type: typing.Literal["apc"], *, lang: typing.Optional[str] = ...
    ) -> list[models.APCShadowSchedule]: ...
    async def get_starrail_lineup_schedules(
        self, type: typing.Literal["moc", "pf", "apc"], *, lang: typing.Optional[str] = None
    ) -> typing.Union[list[models.MOCSchedule], list[models.PureFictionSchedule], list[models.APCShadowSchedule]]:
        """Get the schedule for the HSR lineup simulator."""
        endpoints = {
            "moc": "schedule/list",
            "pf": "story_schedule/list",
            "apc": "boss_schedule/list",
        }
        endpoint = endpoints.get(type)
        if endpoint is None:
            msg = f"Invalid type {type!r} for HSR lineup schedule."
            raise ValueError(msg)

        data = await self._request(endpoint, lang=lang)
        if type == "apc":
            return [models.APCShadowSchedule(**item) for item in data["schedule"]]
        if type == "moc":
            return [models.MOCSchedule(**item) for item in data["schedule"]]
        return [models.PureFictionSchedule(**item) for item in data["schedule"]]
