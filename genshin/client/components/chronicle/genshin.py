"""Genshin battle chronicle component."""

import asyncio
import typing

from genshin import types
from genshin.models.genshin import character as character_models
from genshin.models.genshin import chronicle as models
from genshin.utility import genshin as genshin_utility

from . import base

__all__ = ["GenshinBattleChronicleClient"]


def _get_region(uid: int) -> types.Region:
    return types.Region.CHINESE if genshin_utility.is_chinese(uid) else types.Region.OVERSEAS


class GenshinBattleChronicleClient(base.BaseBattleChronicleClient):
    """Genshin battle chronicle component."""

    async def __get_genshin(
        self,
        endpoint: str,
        uid: int,
        *,
        method: str = "GET",
        lang: typing.Optional[str] = None,
        payload: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        cache: bool = True,
    ) -> typing.Mapping[str, typing.Any]:
        """Get an arbitrary honkai object."""
        payload = dict(payload or {})
        payload.update(role_id=uid, server=genshin_utility.recognize_genshin_server(uid))

        data, params = None, None
        if method == "POST":
            data = payload
        else:
            params = payload

        cache_key: typing.Optional[base.ChronicleCacheKey] = None
        if cache:
            cache_key = base.ChronicleCacheKey(
                types.Game.GENSHIN,
                endpoint,
                uid,
                params=tuple(payload.values()) if payload else (),
                lang=lang or self.lang,
            )

        return await self.request_game_record(
            endpoint,
            lang=lang,
            game=types.Game.GENSHIN,
            region=_get_region(uid),
            params=params,
            data=data,
            cache=cache_key,
        )

    async def get_partial_genshin_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.GenshinPartialUserStats:
        """Get partial genshin user without character equipment."""
        data = await self.__get_genshin("index", uid, lang=lang)
        return models.GenshinPartialUserStats(**data)

    async def get_genshin_characters(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.Character]:
        """Get user characters."""
        data = await self.__get_genshin("character", uid, lang=lang, method="POST")
        return [models.Character(**i) for i in data["avatars"]]

    async def get_genshin_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.GenshinUserStats:
        """Get genshin user."""
        data, character_data = await asyncio.gather(
            self.__get_genshin("index", uid, lang=lang),
            self.__get_genshin("character", uid, lang=lang, method="POST"),
        )
        data = {**data, **character_data}

        return models.GenshinUserStats(**data)

    async def get_genshin_spiral_abyss(
        self,
        uid: int,
        *,
        previous: bool = False,
        lang: typing.Optional[str] = None,
    ) -> models.SpiralAbyss:
        """Get spiral abyss runs."""
        payload = dict(schedule_type=2 if previous else 1)
        data = await self.__get_genshin("spiralAbyss", uid, lang=lang, payload=payload)

        return models.SpiralAbyss(**data)

    async def get_genshin_notes(self, uid: int, *, lang: typing.Optional[str] = None) -> models.Notes:
        """Get the real-time notes."""
        data = await self.__get_genshin("dailyNote", uid, lang=lang, cache=False)
        return models.Notes(**data)

    async def get_genshin_activities(self, uid: int, *, lang: typing.Optional[str] = None) -> models.Activities:
        """Get activities."""
        data = await self.__get_genshin("activities", uid, lang=lang)
        return models.Activities(**data)

    async def get_full_genshin_user(
        self, uid: int, *, lang: typing.Optional[str] = None
    ) -> models.GenshinFullUserStats:
        """Get a user with all their possible data."""
        user, abyss1, abyss2, activities = await asyncio.gather(
            self.get_genshin_user(uid, lang=lang),
            self.get_genshin_spiral_abyss(uid, lang=lang, previous=False),
            self.get_genshin_spiral_abyss(uid, lang=lang, previous=True),
            self.get_genshin_activities(uid, lang=lang),
        )
        abyss = models.SpiralAbyssPair(current=abyss1, previous=abyss2)

        return models.GenshinFullUserStats(**user.dict(), abyss=abyss, activities=activities)

    async def set_top_characters(
        self,
        characters: typing.Sequence[types.IDOr[character_models.BaseCharacter]],
        *,
        uid: typing.Optional[int] = None,
    ) -> None:
        """Set the top 8 visible characters for the current user."""
        uid = uid or await self._get_uid(types.Game.GENSHIN)

        await self.request_game_record(
            "character/top",
            game=types.Game.GENSHIN,
            region=_get_region(uid),
            data=dict(
                avatar_ids=[int(character) for character in characters],
                uid_key=uid,
                server_key=genshin_utility.recognize_genshin_server(uid),
            ),
        )
