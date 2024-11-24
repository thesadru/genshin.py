"""Honkai battle chronicle component."""

import asyncio
import typing

from genshin import errors, types
from genshin.models.honkai import chronicle as models

from . import base

__all__ = ["HonkaiBattleChronicleClient"]


class HonkaiBattleChronicleClient(base.BaseBattleChronicleClient):
    """Honkai battle chronicle component."""

    async def _request_honkai_record(
        self,
        endpoint: str,
        uid: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
        cache: bool = False,
    ) -> typing.Mapping[str, typing.Any]:
        """Get an arbitrary honkai object."""
        uid = uid or await self._get_uid(types.Game.HONKAI)

        cache_key: typing.Optional[base.ChronicleCacheKey] = None
        if cache:
            cache_key = base.ChronicleCacheKey(
                types.Game.HONKAI,
                endpoint,
                uid,
                lang=lang or self.lang,
            )

        account = await self._get_account(types.Game.HONKAI)
        return await self.request_game_record(
            endpoint,
            lang=lang,
            game=types.Game.HONKAI,
            region=self.region,
            params=dict(server=account.server, role_id=uid),
            cache=cache_key,
        )

    async def get_honkai_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.HonkaiUserStats:
        """Get honkai user stats."""
        data = await self._request_honkai_record("index", uid, lang=lang)
        return models.HonkaiUserStats(**data)

    async def get_honkai_battlesuits(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.FullBattlesuit]:
        """Get honkai battlesuits."""
        data = await self._request_honkai_record("characters", uid, lang=lang)
        return [models.FullBattlesuit(**char["character"]) for char in data["characters"]]

    async def get_honkai_old_abyss(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.OldAbyss]:
        """Get honkai old abyss.

        Only for level > 80.
        """
        data = await self._request_honkai_record("latestOldAbyssReport", uid, lang=lang)
        return [models.OldAbyss(**x) for x in data["reports"]]

    async def get_honkai_superstring_abyss(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.SuperstringAbyss]:
        """Get honkai superstring abyss.

        Only for level <= 80.
        """
        data = await self._request_honkai_record("newAbyssReport", uid, lang=lang)
        return [models.SuperstringAbyss(**x) for x in data["reports"]]

    async def get_honkai_abyss(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[typing.Union[models.SuperstringAbyss, models.OldAbyss]]:
        """Get honkai abyss."""
        possible = await asyncio.gather(
            self.get_honkai_old_abyss(uid, lang=lang),
            self.get_honkai_superstring_abyss(uid, lang=lang),
            return_exceptions=True,
        )
        for abyss in possible:
            if not isinstance(abyss, BaseException):
                return abyss
            if not isinstance(abyss, errors.InternalDatabaseError):
                raise abyss from None

        return []

    async def get_honkai_elysian_realm(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.ElysianRealm]:
        """Get honkai elysian realm."""
        data = await self._request_honkai_record("godWar", uid, lang=lang)
        return [models.ElysianRealm(**x) for x in data["records"]]

    async def get_honkai_memorial_arena(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.MemorialArena]:
        """Get honkai memorial arena."""
        data = await self._request_honkai_record("battleFieldReport", uid, lang=lang)
        return [models.MemorialArena(**x) for x in data["reports"]]

    @typing.overload
    async def get_honkai_notes(
        self, uid: int, *, lang: typing.Optional[str] = ..., return_raw_data: typing.Literal[False] = ...
    ) -> models.HonkaiNotes: ...
    @typing.overload
    async def get_honkai_notes(
        self, uid: int, *, lang: typing.Optional[str] = ..., return_raw_data: typing.Literal[True] = ...
    ) -> typing.Mapping[str, typing.Any]: ...
    async def get_honkai_notes(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
        return_raw_data: bool = False,
    ) -> typing.Union[models.HonkaiNotes, typing.Mapping[str, typing.Any]]:
        """Get honkai memorial arena."""
        data = await self._request_honkai_record("note", uid, lang=lang)
        if return_raw_data:
            return data
        return models.HonkaiNotes(**data)

    async def get_full_honkai_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.FullHonkaiUserStats:
        """Get a full honkai user."""
        user, battlesuits, abyss, mr, er = await asyncio.gather(
            self.get_honkai_user(uid, lang=lang),
            self.get_honkai_battlesuits(uid, lang=lang),
            self.get_honkai_abyss(uid, lang=lang),
            self.get_honkai_memorial_arena(uid, lang=lang),
            self.get_honkai_elysian_realm(uid, lang=lang),
        )

        return models.FullHonkaiUserStats(
            **user.model_dump(by_alias=True),
            battlesuits=battlesuits,
            abyss=abyss,
            memorial_arena=mr,
            elysian_realm=er,
        )

    get_old_abyss = get_honkai_old_abyss
    get_superstring_abyss = get_honkai_superstring_abyss
    get_elysian_realm = get_honkai_elysian_realm
    get_memorial_arena = get_honkai_memorial_arena
