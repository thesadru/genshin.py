import typing

import aiohttp.typedefs

from genshin import types
from genshin.client import routes
from genshin.client.components import base
from genshin.constants import GAME_LANGS
from genshin.models.starrail import rpgsimulator as models
from genshin.utility import ds
from genshin.utility.uid import recognize_server

__all__ = ("HSRLineupClient",)

LineupGameMode = typing.Union[models.StarRailGameModeType, typing.Literal["Chasm", "Story", "Boss"]]


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

    def get_starrail_lineup_floor(
        self,
        game_modes: typing.Sequence[models.StarRailGameMode],
        *,
        type: LineupGameMode,
        floor: int,
    ) -> typing.Optional[models.StarRailGameModeFloor]:
        """Get a specific floor from the game modes."""
        for mode in game_modes:
            if mode.type != type:
                continue
            for f in mode.floors:
                if f.floor == floor:
                    return f

        return None

    @typing.overload
    async def get_starrail_lineups(
        self,
        *,
        tag_id: int,
        group_id: int,
        type: typing.Union[typing.Literal[models.StarRailGameModeType.MOC], typing.Literal["Chasm"]],
        next_page_token: typing.Optional[str] = ...,
        order: typing.Literal["Hot", "Match", "CreatedTime"] = ...,
        lang: typing.Optional[str] = ...,
    ) -> models.StarRailLineupResponse: ...
    @typing.overload
    async def get_starrail_lineups(
        self,
        *,
        tag_id: int,
        group_id: int,
        type: typing.Union[typing.Literal[models.StarRailGameModeType.PURE_FICTION], typing.Literal["Story"]],
        next_page_token: typing.Optional[str] = ...,
        order: typing.Literal["Hot", "Match", "CreatedTime"] = ...,
        lang: typing.Optional[str] = ...,
    ) -> models.PureFictionLineupResponse: ...
    @typing.overload
    async def get_starrail_lineups(
        self,
        *,
        tag_id: int,
        group_id: int,
        type: typing.Union[typing.Literal[models.StarRailGameModeType.APC_SHADOW], typing.Literal["Boss"]],
        next_page_token: typing.Optional[str] = ...,
        order: typing.Literal["Hot", "Match", "CreatedTime"] = ...,
        lang: typing.Optional[str] = ...,
    ) -> models.APCShadowLineupResponse: ...
    async def get_starrail_lineups(
        self,
        *,
        tag_id: int,
        group_id: int,
        type: LineupGameMode,
        next_page_token: typing.Optional[str] = None,
        order: typing.Literal["Hot", "Match", "CreatedTime"] = "Match",
        lang: typing.Optional[str] = None,
    ) -> typing.Union[models.StarRailLineupResponse, models.PureFictionLineupResponse, models.APCShadowLineupResponse]:
        """Get the available lineups for the HSR lineup simulator."""
        params: dict[str, typing.Any] = {
            "tag_id": tag_id,
            "group_id": group_id,
            "lineup_type": str(type),
            "game": "hkrpg",
        }

        if order not in {"Hot", "Match", "CreatedTime"}:
            msg = f"Invalid order {order!r}. Must be one of 'Hot', 'Match', or 'CreatedTime'."
            raise ValueError(msg)
        params["order"] = order

        if self.uid is not None:
            params["uid"] = self.uid
            params["region"] = recognize_server(self.uid, types.Game.STARRAIL)

        if next_page_token:
            params["next_page_token"] = next_page_token

        data = await self._request("lineup/index", lang=lang, params=params)

        if type == "Story":
            return models.PureFictionLineupResponse(**data)
        elif type == "Boss":
            return models.APCShadowLineupResponse(**data)
        return models.StarRailLineupResponse(**data)

    @typing.overload
    async def get_starrail_lineup_schedules(
        self,
        type: typing.Union[typing.Literal[models.StarRailGameModeType.MOC], typing.Literal["Chasm"]],
        *,
        lang: typing.Optional[str] = ...,
    ) -> list[models.MOCSchedule]: ...
    @typing.overload
    async def get_starrail_lineup_schedules(
        self,
        type: typing.Union[typing.Literal[models.StarRailGameModeType.PURE_FICTION], typing.Literal["Story"]],
        *,
        lang: typing.Optional[str] = ...,
    ) -> list[models.PureFictionSchedule]: ...
    @typing.overload
    async def get_starrail_lineup_schedules(
        self,
        type: typing.Union[typing.Literal[models.StarRailGameModeType.APC_SHADOW], typing.Literal["Boss"]],
        *,
        lang: typing.Optional[str] = ...,
    ) -> list[models.APCShadowSchedule]: ...
    async def get_starrail_lineup_schedules(
        self, type: LineupGameMode, *, lang: typing.Optional[str] = None
    ) -> typing.Union[list[models.MOCSchedule], list[models.PureFictionSchedule], list[models.APCShadowSchedule]]:
        """Get the schedule for the HSR lineup simulator."""
        endpoints = {
            "Chasm": "schedule/list",
            "Story": "story_schedule/list",
            "Boss": "boss_schedule/list",
        }
        endpoint = endpoints.get(type)
        if endpoint is None:
            msg = f"Invalid type {type!r} for HSR lineup schedule."
            raise ValueError(msg)

        data = await self._request(endpoint, lang=lang)
        if type == "Boss":
            return [models.APCShadowSchedule(**item) for item in data["schedule"]]
        if type == "Chasm":
            return [models.MOCSchedule(**item) for item in data["schedule"]]
        return [models.PureFictionSchedule(**item) for item in data["schedule"]]
