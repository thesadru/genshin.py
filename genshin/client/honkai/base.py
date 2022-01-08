from __future__ import annotations

import asyncio
from typing import *

from genshin import models as base_models
from genshin.client import adapter, base
from genshin.models import honkai as hmodels

from genshin.utils.honkai import recognize_honkai_server  # temp import

CallableT = TypeVar("CallableT", bound=Callable[..., Any])


class BaseHonkaiClient(base.APIClient):
    async def honkai_accounts(self, *, lang: str = None) -> List[base_models.GameAccount]:
        """Get the Honkai accounts of the currently logged-in user

        :params lang: The language to use
        """
        return [
            account
            for account in await self.get_game_accounts(lang=lang)
            if account.game is base_models.Game.honkai
        ]

    # GAME RECORD

    async def _fetch_raw_user(self, uid: int, lang: str = None) -> Dict[str, Any]:
        """Low-level http method for fetching the game record index"""
        server = recognize_honkai_server(uid)
        data = await self.request_game_record(
            "honkai3rd/api/index",
            lang=lang,
            params=dict(server=server, role_id=uid),
        )
        return data

    async def _fetch_raw_characters(self, uid: int, *, lang: str = None) -> List[Dict[str, Any]]:
        """Low-level http method for fetching the game record characters"""
        server = recognize_honkai_server(uid)
        data = await self.request_game_record(
            "honkai3rd/api/characters", lang=lang, params=dict(server=server, role_id=uid)
        )

        return data["characters"]

    async def get_record_card(
        self, hoyolab_uid: int, *, lang: str = None
    ) -> List[hmodels.HonkaiRecordCard]:
        """Get a user's Honkai record card(s)

        :param hoyolab_uid: A hoyolab uid
        :param lang: The language to use
        """
        cards = await self.get_record_cards(hoyolab_uid, lang=lang)
        return [card for card in cards if isinstance(card, hmodels.HonkaiRecordCard)]

    async def get_user(self, uid: int, *, lang: str = None) -> hmodels.HonkaiUserStats:
        """Get a user's stats and characters

        :param uid: A Honkai uid
        :param character_ids: The ids of characters you want to fetch
        :param lang: The language to use
        """
        data, data["battlesuits"] = await asyncio.gather(
            self._fetch_raw_user(uid, lang=lang),
            self._fetch_raw_characters(uid, lang=lang),
        )

        return hmodels.HonkaiUserStats(**data)

    async def get_partial_user(
        self, uid: int, *, lang: str = None
    ) -> hmodels.HonkaiPartialUserStats:
        """Helper function to get a user without any equipment

        :param uid: A Honkai uid
        :param lang: The language to use
        """
        data = await self._fetch_raw_user(uid, lang=lang)
        return hmodels.HonkaiPartialUserStats(**data)

    async def get_battlesuits(self, uid: int, *, lang: str = None) -> List[hmodels.FullBattlesuit]:
        """Helper function to fetch all battlesuits with equipment owned by a user
        :param uid: A Honkai uid
        :param lang: The language to use
        """
        data = await self._fetch_raw_characters(uid, lang=lang)
        return [hmodels.FullBattlesuit(**i) for i in data]

    async def get_superstring_abyss(
        self, uid: int, *, lang: str = None
    ) -> List[hmodels.SuperstringAbyss]:
        """Get Honkai abyss runs for Superstring Abyss only (lv 81+)

        :param uid: A Honkai uid
        :param lang: The language to use
        """
        server = recognize_honkai_server(uid)
        data = await self.request_game_record(
            "honkai3rd/api/newAbyssReport",
            lang=lang,
            params=dict(role_id=uid, server=server),
        )
        return [hmodels.SuperstringAbyss(**report) for report in data["reports"]]

    async def get_old_abyss(self, uid: int, *, lang: str = None) -> List[hmodels.OldAbyss]:
        """Get Honkai abyss runs for Q-Singularis and Dirac Sea only (lv 25 ~ 80)

        :param uid: A Honkai uid
        :param lang: The language to use
        """
        server = recognize_honkai_server(uid)
        data = await self.request_game_record(
            "honkai3rd/api/latestOldAbyssReport",
            lang=lang,
            params=dict(role_id=uid, server=server),
        )
        return [hmodels.OldAbyss(**report) for report in data["reports"]]

    async def get_abyss(
        self, uid: int, *, lang: str = None
    ) -> List[Union[hmodels.SuperstringAbyss, hmodels.OldAbyss]]:
        """Get all possible types of Abyss runs.

        Note: this makes two API requests.
        It is recommended to call either `get_superstring_abyss` or `get_old_abyss` instead
        if the level of the target user is known, to save on one API request.

        :param uid: A Honkai uid
        :param lang: The language to use
        """
        data = await asyncio.gather(
            self.get_superstring_abyss(uid, lang=lang),
            self.get_old_abyss(uid, lang=lang),
            return_exceptions=True,
        )
        return [run for mode in data if not isinstance(mode, BaseException) for run in mode]

    async def get_memorial_arena(
        self, uid: int, *, lang: str = None
    ) -> List[hmodels.MemorialArena]:
        """Get a list of Memorial Arena data rotations for the user

        :param uid: A Honkai uid
        :param lang: The language to use
        """
        server = recognize_honkai_server(uid)
        data = await self.request_game_record(
            "honkai3rd/api/battleFieldReport",
            lang=lang,
            params=dict(role_id=uid, server=server),
        )
        return [hmodels.MemorialArena(**report) for report in data["reports"]]

    async def get_elysian_realm(self, uid: int, *, lang: str = None) -> hmodels.ElysianRealms:
        """Get a list of Elysian Realm runs for the user

        :param uid: A Honkai uid
        :param lang: The language to use
        """
        server = recognize_honkai_server(uid)
        data = await self.request_game_record(
            "honkai3rd/api/godWar",
            lang=lang,
            params=dict(role_id=uid, server=server),
        )
        return hmodels.ElysianRealms(**data)

    async def get_full_user(self, uid: int, *, lang: str = None) -> hmodels.HonkaiFullUserStats:
        """Get a user with all their possible data

        :param uid: A Honkai uid
        :param lang: The language to use
        """
        user_data, battlesuits, abyss, ma, er = await asyncio.gather(
            self._fetch_raw_user(uid, lang=lang),
            self.get_battlesuits(uid, lang=lang),
            self.get_abyss(uid, lang=lang),
            self.get_memorial_arena(uid, lang=lang),
            self.get_elysian_realm(uid, lang=lang),
        )
        return hmodels.HonkaiFullUserStats(
            **user_data, battlesuits=battlesuits, abyss=abyss, memorial_arena=ma, elysian_realm=er
        )
