"""Hoyolab component."""
import typing

from genshin import types
from genshin.client import cache as client_cache
from genshin.client import manager, routes
from genshin.client.components import base
from genshin.models import hoyolab as models
from genshin.utility import genshin as genshin_utility

__all__ = ["HoyolabClient"]


class HoyolabClient(base.BaseClient):
    """Hoyolab component."""

    async def search_users(self, keyword: str) -> typing.Sequence[models.SearchUser]:
        """Search hoyolab users."""
        data = await self.request_hoyolab(
            "community/search/wapi/search/user",
            params=dict(keyword=keyword, page_size=20),
            cache=client_cache.cache_key("search", keyword=keyword),
        )
        return [models.SearchUser(**i["user"]) for i in data["list"]]

    async def get_recommended_users(self, *, limit: int = 200) -> typing.Sequence[models.SearchUser]:
        """Get a list of recommended active users."""
        data = await self.request_hoyolab(
            "community/user/wapi/recommendActive",
            params=dict(page_size=limit),
            cache=client_cache.cache_key("recommended"),
        )
        return [models.SearchUser(**i["user"]) for i in data["list"]]

    @manager.no_multi
    async def redeem_code(
        self,
        code: str,
        uid: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
    ) -> None:
        """Redeems a gift code for the current genshin user."""
        uid = uid or await self._get_uid(types.Game.GENSHIN)

        await self.request(
            routes.CODE_URL.get_url(),
            params=dict(
                uid=uid,
                region=genshin_utility.recognize_genshin_server(uid),
                cdkey=code,
                game_biz="hk4e_global",
                lang=genshin_utility.create_short_lang_code(lang or self.lang),
            ),
        )
