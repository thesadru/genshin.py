"""Honkai battle chronicle component."""

import asyncio
import typing

from genshin import types
from genshin.models.honkai import chronicle as models
from genshin.utility import honkai as honkai_utility

from . import base

__all__ = ["HonkaiBattleChronicleClient"]


class HonkaiBattleChronicleClient(base.BaseBattleChronicleClient):
    """Honkai battle chronicle component."""

    async def __get_honkai(
        self,
        endpoint: str,
        uid: int,
        lang: typing.Optional[str] = None,
    ) -> typing.Mapping[str, typing.Any]:
        """Get an arbitrary honkai object."""
        return await self.request_game_record(
            endpoint,
            lang=lang,
            game=types.Game.HONKAI,
            region=types.Region.OVERSEAS,
            params=dict(role_id=uid, server=honkai_utility.recognize_honkai_server(uid)),
        )

    async def get_honkai_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.HonkaiUserStats:
        """Get honkai user stats."""
        data = await self.__get_honkai("index", uid, lang=lang)
        return models.HonkaiUserStats(**data)

    async def get_honkai_battlesuits(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.FullBattlesuit]:
        """Get honkai battlesuits."""
        data = await self.__get_honkai("characters", uid, lang=lang)
        return [models.FullBattlesuit(**char["character"]) for char in data["characters"]]

    async def get_honkai_abyss(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.SuperstringAbyss]:
        """Get honkai abyss."""
        data = await self.__get_honkai("newAbyssReport", uid, lang=lang)
        return [models.SuperstringAbyss(**x) for x in data["reports"]]

    async def get_honkai_elysian_realm(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.ElysianRealm]:
        """Get honkai elysian realm."""
        data = await self.__get_honkai("godWar", uid, lang=lang)
        return [models.ElysianRealm(**x) for x in data["records"]]

    async def get_honkai_memorial_arena(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.MemorialArena]:
        """Get honkai memorial arena."""
        data = await self.__get_honkai("battleFieldReport", uid, lang=lang)
        return [models.MemorialArena(**x) for x in data["reports"]]

    async def get_full_honkai_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.HonkaiFullUserStats:
        """Get a full honkai user."""
        user, battlesuits, abyss, mr, er = await asyncio.gather(
            self.get_honkai_user(uid, lang=lang),
            self.get_honkai_battlesuits(uid, lang=lang),
            self.get_honkai_abyss(uid, lang=lang),
            self.get_honkai_memorial_arena(uid, lang=lang),
            self.get_honkai_elysian_realm(uid, lang=lang),
        )

        return models.HonkaiFullUserStats(
            **user.dict(),
            battlesuits=battlesuits,
            abyss=abyss,
            memorial_arena=mr,
            elysian_realm=er,
        )
