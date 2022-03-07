"""Honkai battle chronicle component."""

import typing

from genshin import types
from genshin.utility import honkai as honkai_utility

from . import base


class HonkaiBattleChronicleClient(base.BaseBattleChronicleClient):
    """Honkai battle chronicle component."""

    async def get_honkai_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ):
        """Low-level http method for fetching the game record index."""
        data = await self.request_game_record(
            "index",
            lang=lang,
            game=types.Game.HONKAI,
            region=types.Region.OVERSEAS,
            params=dict(role_id=uid, server=honkai_utility.recognize_honkai_server(uid)),
        )
        return data
