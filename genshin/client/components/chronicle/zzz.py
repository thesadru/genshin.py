"""StarRail battle chronicle component."""

import asyncio
import typing

from genshin import errors, types, utility
from genshin.client import routes
from genshin.models import zzz as models

from . import base

__all__ = ("ZZZBattleChronicleClient",)


class ZZZBattleChronicleClient(base.BaseBattleChronicleClient):
    """ZZZ battle chronicle component."""

    async def _request_zzz_record(
        self,
        endpoint: str,
        uid: typing.Optional[int] = None,
        *,
        method: str = "GET",
        lang: typing.Optional[str] = None,
        payload: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        cache: bool = False,
        is_nap_ledger: bool = False,
        is_special_payload: bool = False,
    ) -> typing.Mapping[str, typing.Any]:
        """Get an arbitrary ZZZ object."""
        payload = dict(payload or {})
        original_payload = payload.copy()

        uid = uid or await self._get_uid(types.Game.ZZZ)

        if is_nap_ledger or is_special_payload:
            payload = {
                "uid": uid,
                "region": utility.recognize_zzz_server(uid),
                **payload,
            }
        else:
            payload = {
                "role_id": uid,
                "server": utility.recognize_zzz_server(uid),
                **payload,
            }

        data, params = None, None
        if method == "POST":
            data = payload
        else:
            params = payload

        cache_key: typing.Optional[base.ChronicleCacheKey] = None
        if cache:
            cache_key = base.ChronicleCacheKey(
                types.Game.ZZZ,
                endpoint,
                uid,
                lang=lang or self.lang,
                params=tuple(original_payload.values()),
            )

        return await self.request_game_record(
            endpoint,
            lang=lang,
            game=types.Game.ZZZ,
            region=utility.recognize_region(uid, game=types.Game.ZZZ),
            params=params,
            data=data,
            cache=cache_key,
            custom_route=routes.NAP_LEDGER_URL if is_nap_ledger else None,
        )

    @typing.overload
    async def get_zzz_notes(
        self,
        uid: typing.Optional[int] = ...,
        *,
        lang: typing.Optional[str] = ...,
        autoauth: bool = ...,
        return_raw_data: typing.Literal[False] = ...,
    ) -> models.ZZZNotes: ...
    @typing.overload
    async def get_zzz_notes(
        self,
        uid: typing.Optional[int] = ...,
        *,
        lang: typing.Optional[str] = ...,
        autoauth: bool = ...,
        return_raw_data: typing.Literal[True] = ...,
    ) -> typing.Mapping[str, typing.Any]: ...
    async def get_zzz_notes(
        self,
        uid: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
        autoauth: bool = True,
        return_raw_data: bool = False,
    ) -> typing.Union[models.ZZZNotes, typing.Mapping[str, typing.Any]]:
        """Get ZZZ sticky notes (real-time notes)."""
        try:
            data = await self._request_zzz_record("note", uid, lang=lang)
        except errors.DataNotPublic as e:
            # error raised only when real-time notes are not enabled
            if uid and (await self._get_uid(types.Game.ZZZ)) != uid:
                raise errors.GenshinException(e.response, "Cannot view real-time notes of other users.") from e
            if not autoauth:
                raise errors.GenshinException(e.response, "Real-time notes are not enabled.") from e

            await self.update_settings(3, True, game=types.Game.ZZZ)
            data = await self._request_zzz_record("note", uid, lang=lang)

        if return_raw_data:
            return data
        return models.ZZZNotes(**data)

    async def get_zzz_diary(
        self,
        uid: typing.Optional[int] = None,
        *,
        month: typing.Optional[str] = None,
        lang: typing.Optional[str] = None,
    ) -> models.ZZZDiary:
        """Get ZZZ inter-knot monthly earning data."""
        data = await self._request_zzz_record(
            "month_info", uid, lang=lang, payload={"month": month or ""}, is_nap_ledger=True
        )
        return models.ZZZDiary(**data)

    async def get_zzz_diary_detail(
        self,
        month: str,
        *,
        type: models.ZZZCurrencyType,
        page: int = 1,
        page_size: int = 20,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> models.ZZZDiaryDetail:
        """Get ZZZ inter-knot monthly earning data."""
        if not month:
            raise ValueError("month is required.")

        data = await self._request_zzz_record(
            "month_detail",
            uid,
            lang=lang,
            payload={"month": month, "current_page": page, "type": type.value, "page_size": page_size},
            is_nap_ledger=True,
        )
        return models.ZZZDiaryDetail(**data)

    async def get_zzz_user(
        self,
        uid: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.ZZZUserStats:
        """Get ZZZ user stats."""
        data = await self._request_zzz_record("index", uid, lang=lang)
        return models.ZZZUserStats(**data)

    async def get_zzz_agents(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> typing.Sequence[models.ZZZPartialAgent]:
        """Get all owned ZZZ characters (only brief info)."""
        data = await self._request_zzz_record("avatar/basic", uid, lang=lang)
        return [models.ZZZPartialAgent(**item) for item in data["avatar_list"]]

    async def get_bangboos(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> typing.Sequence[models.ZZZBaseBangboo]:
        """Get all owned ZZZ bangboos."""
        data = await self._request_zzz_record("buddy/info", uid, lang=lang)
        return [models.ZZZBaseBangboo(**item) for item in data["list"]]

    @typing.overload
    async def get_zzz_agent_info(
        self,
        character_id: int,
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> models.ZZZFullAgent: ...
    @typing.overload
    async def get_zzz_agent_info(
        self,
        character_id: typing.Sequence[int],
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.ZZZFullAgent]: ...
    async def get_zzz_agent_info(
        self,
        character_id: typing.Union[int, typing.Sequence[int]],
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Union[models.ZZZFullAgent, typing.Sequence[models.ZZZFullAgent]]:
        """Get a ZZZ character's detailed info."""
        if isinstance(character_id, typing.Sequence):
            tasks = [
                self._request_zzz_record("avatar/info", uid, lang=lang, payload={"id_list[]": character_id_})
                for character_id_ in character_id
            ]
            results = await asyncio.gather(*tasks)
            return [models.ZZZFullAgent(**data["avatar_list"][0]) for data in results]

        data = await self._request_zzz_record("avatar/info", uid, lang=lang, payload={"id_list[]": character_id})
        return models.ZZZFullAgent(**data["avatar_list"][0])

    @typing.overload
    async def get_shiyu_defense(
        self,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[False] = ...,
    ) -> models.ShiyuDefense: ...
    @typing.overload
    async def get_shiyu_defense(
        self,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[True] = ...,
    ) -> typing.Mapping[str, typing.Any]: ...
    async def get_shiyu_defense(
        self,
        uid: typing.Optional[int] = None,
        *,
        previous: bool = False,
        lang: typing.Optional[str] = None,
        raw: bool = False,
    ) -> typing.Union[models.ShiyuDefense, typing.Mapping[str, typing.Any]]:
        """Get ZZZ Shiyu defense stats."""
        payload = {"schedule_type": 2 if previous else 1, "need_all": "true"}
        data = await self._request_zzz_record("challenge", uid, lang=lang, payload=payload)
        if raw:
            return data
        return models.ShiyuDefense(**data)

    @typing.overload
    async def get_deadly_assault(
        self,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[False] = ...,
    ) -> models.DeadlyAssault: ...
    @typing.overload
    async def get_deadly_assault(
        self,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[True] = ...,
    ) -> typing.Mapping[str, typing.Any]: ...
    async def get_deadly_assault(
        self,
        uid: typing.Optional[int] = None,
        *,
        previous: bool = False,
        lang: typing.Optional[str] = None,
        raw: bool = False,
    ) -> typing.Union[models.DeadlyAssault, typing.Mapping[str, typing.Any]]:
        """Get ZZZ Shiyu defense stats."""
        payload = {"schedule_type": 2 if previous else 1}
        data = await self._request_zzz_record("mem_detail", uid, lang=lang, payload=payload, is_special_payload=True)
        if raw:
            return data
        return models.DeadlyAssault(**data)

    async def get_lost_void_summary(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> models.LostVoidSummary:
        """Get ZZZ Lost Void summary."""
        data = await self._request_zzz_record("abysss2_abstract", uid, lang=lang, is_special_payload=True)
        return models.LostVoidSummary(**data)
