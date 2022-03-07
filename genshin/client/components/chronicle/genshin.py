"""Genshin battle chronicle component."""

import typing

from genshin import types
from genshin.models.genshin import chronicle as models
from genshin.utility import genshin as genshin_utility

from . import base


def _get_region(uid: int) -> types.Region:
    return types.Region.CHINESE if genshin_utility.is_chinese(uid) else types.Region.OVERSEAS


class GenshinBattleChronicleClient(base.BaseBattleChronicleClient):
    """Genshin battle chronicle component."""

    async def get_genshin_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.GenshinPartialUserStats:
        """Low-level http method for fetching the game record index."""
        data = await self.request_game_record(
            "index",
            lang=lang,
            game=types.Game.GENSHIN,
            region=_get_region(uid),
            params=dict(role_id=uid, server=genshin_utility.recognize_genshin_server(uid)),
        )
        return models.GenshinPartialUserStats(**data)
