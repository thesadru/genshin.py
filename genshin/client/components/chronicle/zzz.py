"""StarRail battle chronicle component."""

import typing

from genshin import errors, types, utility
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
        cache: bool = True,
    ) -> typing.Mapping[str, typing.Any]:
        """Get an arbitrary ZZZ object."""
        payload = dict(payload or {})
        original_payload = payload.copy()

        uid = uid or await self._get_uid(types.Game.ZZZ)
        payload = dict(role_id=uid, server=utility.recognize_zzz_server(uid), **payload)

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
        )

    async def get_zzz_notes(
        self,
        uid: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
        autoauth: bool = True,
    ) -> models.ZZZNotes:
        """Get ZZZ sticky notes (real-time notes)."""
        try:
            data = await self._request_zzz_record("note", uid, lang=lang, cache=False)
        except errors.DataNotPublic as e:
            # error raised only when real-time notes are not enabled
            if uid and (await self._get_uid(types.Game.ZZZ)) != uid:
                raise errors.GenshinException(e.response, "Cannot view real-time notes of other users.") from e
            if not autoauth:
                raise errors.GenshinException(e.response, "Real-time notes are not enabled.") from e

            await self.update_settings(3, True, game=types.Game.ZZZ)
            data = await self._request_zzz_record("note", uid, lang=lang, cache=False)

        return models.ZZZNotes(**data)

    async def get_zzz_user(
        self,
        uid: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.ZZZUserStats:
        """Get ZZZ user stats."""
        data = await self._request_zzz_record("index", uid, lang=lang, cache=False)
        return models.ZZZUserStats(**data)

    async def get_zzz_characters(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> typing.Sequence[models.ZZZPartialAgent]:
        """Get all owned ZZZ characters (only brief info)."""
        data = await self._request_zzz_record("avatar/basic", uid, lang=lang, cache=False)
        return [models.ZZZPartialAgent(**item) for item in data["avatar_list"]]

    async def get_bangboos(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> typing.Sequence[models.ZZZBaseBangboo]:
        """Get all owned ZZZ bangboos."""
        data = await self._request_zzz_record("buddy/info", uid, lang=lang, cache=False)
        return [models.ZZZBaseBangboo(**item) for item in data["list"]]

    @typing.overload
    async def get_zzz_character(
        self,
        character_id: int,
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> models.ZZZFullAgent: ...
    @typing.overload
    async def get_zzz_character(
        self,
        character_id: typing.Sequence[int],
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.ZZZFullAgent]: ...
    async def get_zzz_character(
        self,
        character_id: typing.Union[int, typing.Sequence[int]],
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Union[models.ZZZFullAgent, typing.Sequence[models.ZZZFullAgent]]:
        """Get a ZZZ character's detailed info."""
        if isinstance(character_id, list):
            character_id = tuple(character_id)

        data = await self._request_zzz_record("avatar/info", uid, lang=lang, payload={"is_list[]": character_id})
        if isinstance(character_id, int):
            return models.ZZZFullAgent(**data["avatar_list"][0])
        return [models.ZZZFullAgent(**item) for item in data["avatar_list"]]
