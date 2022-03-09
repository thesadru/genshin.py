"""Genshin battle chronicle component."""

import asyncio
import typing

from genshin import types
from genshin.models.genshin import character as character_models
from genshin.models.genshin import chronicle as models
from genshin.utility import genshin as genshin_utility

from . import base


def _get_region(uid: int) -> types.Region:
    return types.Region.CHINESE if genshin_utility.is_chinese(uid) else types.Region.OVERSEAS


class GenshinBattleChronicleClient(base.BaseBattleChronicleClient):
    """Genshin battle chronicle component."""

    async def get_partial_genshin_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.GenshinPartialUserStats:
        """Get partial genshin user without character equipment."""
        data = await self.request_game_record(
            "index",
            lang=lang,
            game=types.Game.GENSHIN,
            region=_get_region(uid),
            params=dict(role_id=uid, server=genshin_utility.recognize_genshin_server(uid)),
        )
        return models.GenshinPartialUserStats(**data)

    async def get_genshin_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.GenshinUserStats:
        """Get genshin user."""
        data, character_data = await asyncio.gather(
            self.request_game_record(
                "index",
                lang=lang,
                game=types.Game.GENSHIN,
                region=_get_region(uid),
                params=dict(role_id=uid, server=genshin_utility.recognize_genshin_server(uid)),
            ),
            self.request_game_record(
                "character",
                lang=lang,
                game=types.Game.GENSHIN,
                region=_get_region(uid),
                method="POST",
                data=dict(role_id=str(uid), server=genshin_utility.recognize_genshin_server(uid)),
            ),
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
        schedule_type = 2 if previous else 1
        data = await self.request_game_record(
            "spiralAbyss",
            lang=lang,
            game=types.Game.GENSHIN,
            region=_get_region(uid),
            params=dict(role_id=uid, server=genshin_utility.recognize_genshin_server(uid), schedule_type=schedule_type),
        )
        return models.SpiralAbyss(**data)

    async def get_genshin_notes(self, uid: int, *, lang: typing.Optional[str] = None) -> models.Notes:
        """Get the real-time notes."""
        data = await self.request_game_record(
            "dailyNote",
            lang=lang,
            game=types.Game.GENSHIN,
            region=_get_region(uid),
            params=dict(role_id=uid, server=genshin_utility.recognize_genshin_server(uid)),
        )
        return models.Notes(**data)

    async def get_genshin_activities(self, uid: int, *, lang: typing.Optional[str] = None) -> models.Activities:
        """Get activities."""
        data = await self.request_game_record(
            "activities",
            lang=lang,
            game=types.Game.GENSHIN,
            region=_get_region(uid),
            params=dict(role_id=uid, server=genshin_utility.recognize_genshin_server(uid)),
        )
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
        payload: typing.Dict[str, typing.Any] = dict(avatar_ids=[int(character) for character in characters])
        payload.update(await self._complete_uid(types.Game.GENSHIN, uid, uid_key="role_id", server_key="server"))

        await self.request_game_record(
            "character/top",
            game=types.Game.GENSHIN,
            region=_get_region(payload["role_id"]),
            data=payload,
        )
