"""Hoyolab component."""

import asyncio
import typing
import warnings

from genshin import types, utility
from genshin.client import cache as client_cache
from genshin.client import routes
from genshin.client.components import base
from genshin.client.manager import managers
from genshin.models import hoyolab as models

__all__ = ["HoyolabClient"]


class HoyolabClient(base.BaseClient):
    """Hoyolab component."""

    async def _get_server_region(self, uid: int, game: types.Game) -> str:
        """Fetch the server region of an account from the API."""
        data = await self.request(
            routes.GET_USER_REGION_URL.get_url(),
            params=dict(game_biz=utility.get_prod_game_biz(self.region, game)),
            cache=client_cache.cache_key("server_region", game=game, uid=uid, region=self.region),
        )
        for account in data["list"]:
            if account["game_uid"] == str(uid):
                return account["region"]

        raise ValueError(f"Failed to recognize server for game {game!r} and uid {uid!r}")

    async def _request_announcements(
        self,
        game: types.Game,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.Announcement]:
        """Get a list of game announcements."""
        if game is types.Game.GENSHIN:
            params = dict(
                game="hk4e",
                game_biz="hk4e_global",
                bundle_id="hk4e_global",
                platform="pc",
                region=utility.recognize_genshin_server(uid),
                uid=uid,
                level=8,
                lang=lang or self.lang,
            )
            url = routes.HK4E_URL.get_url()
        elif game is types.Game.ZZZ:
            params = dict(
                game="nap",
                game_biz="nap_global",
                bundle_id="nap_global",
                platform="pc",
                region=utility.recognize_zzz_server(uid),
                level=60,
                lang=lang or self.lang,
                uid=uid,
            )
            url = routes.NAP_URL.get_url()
        elif game is types.Game.STARRAIL:
            params = dict(
                game="hkrpg",
                game_biz="hkrpg_global",
                bundle_id="hkrpg_global",
                platform="pc",
                region=utility.recognize_starrail_server(uid),
                uid=uid,
                level=70,
                lang=lang or self.lang,
                channel_id=1,
            )
            url = routes.HKRPG_URL.get_url()
        else:
            msg = f"{game!r} is not supported yet."
            raise ValueError(msg)

        info, details = await asyncio.gather(
            self.request_hoyolab(
                url / "announcement/api/getAnnList",
                lang=lang,
                params=params,
                static_cache=client_cache.cache_key("announcements", endpoint="info", lang=lang or self.lang),
            ),
            self.request_hoyolab(
                url / "announcement/api/getAnnContent",
                lang=lang,
                params=params,
                static_cache=client_cache.cache_key("announcements", endpoint="details", lang=lang or self.lang),
            ),
        )

        announcements: typing.List[typing.Mapping[str, typing.Any]] = []
        extra_list: typing.List[typing.Mapping[str, typing.Any]] = (
            info["pic_list"][0]["type_list"] if "pic_list" in info and info["pic_list"] else []
        )
        for sublist in info["list"] + extra_list:
            for info in sublist["list"]:
                detail = next((i for i in details["list"] if i["ann_id"] == info["ann_id"]), None)
                announcements.append({**info, **(detail or {})})

        return [models.Announcement(**i) for i in announcements]

    async def search_users(
        self,
        keyword: str,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.PartialHoyolabUser]:
        """Search hoyolab users."""
        data = await self.request_bbs(
            "community/search/wapi/search/user",
            lang=lang,
            params=dict(keyword=keyword, page_size=20),
            cache=client_cache.cache_key("search", keyword=keyword, lang=self.lang),
        )
        return [models.PartialHoyolabUser(**i["user"]) for i in data["list"]]

    async def get_hoyolab_user(
        self,
        hoyolab_id: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.FullHoyolabUser:
        """Get a hoyolab user."""
        if self.region == types.Region.OVERSEAS:
            url = "/community/painter/wapi/user/full"
        elif self.region == types.Region.CHINESE:
            url = "/user/wapi/getUserFullInfo"
        else:
            raise TypeError(f"{self.region!r} is not a valid region.")

        data = await self.request_bbs(
            url=url,
            lang=lang,
            params=dict(uid=hoyolab_id) if hoyolab_id else None,
            cache=client_cache.cache_key("hoyolab", uid=hoyolab_id, lang=lang or self.lang),
        )
        return models.FullHoyolabUser(**data["user_info"])

    async def get_recommended_users(self, *, limit: int = 200) -> typing.Sequence[models.PartialHoyolabUser]:
        """Get a list of recommended active users."""
        data = await self.request_bbs(
            "community/user/wapi/recommendActive",
            params=dict(page_size=limit),
            cache=client_cache.cache_key("recommended"),
        )
        return [models.PartialHoyolabUser(**i["user"]) for i in data["list"]]

    async def get_genshin_announcements(
        self,
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.Announcement]:
        """Get a list of Genshin Impact announcements."""
        if self.cookie_manager.multi:
            uid = uid or await self._get_uid(types.Game.GENSHIN)
        else:
            uid = 900000005
        return await self._request_announcements(types.Game.GENSHIN, uid, lang=lang)

    async def get_zzz_announcements(
        self,
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.Announcement]:
        """Get a list of Zenless Zone Zero announcements."""
        if self.cookie_manager.multi:
            uid = uid or await self._get_uid(types.Game.ZZZ)
        else:
            uid = 1300000000
        return await self._request_announcements(types.Game.ZZZ, uid, lang=lang)

    async def get_starrail_announcements(
        self,
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.Announcement]:
        """Get a list of Star Rail announcements."""
        if self.cookie_manager.multi:
            uid = uid or await self._get_uid(types.Game.STARRAIL)
        else:
            uid = 809162009
        return await self._request_announcements(types.Game.STARRAIL, uid, lang=lang)

    @managers.requires_cookie_token
    async def redeem_code(
        self,
        code: str,
        uid: typing.Optional[int] = None,
        *,
        game: typing.Optional[types.Game] = None,
        lang: typing.Optional[str] = None,
        region: typing.Optional[str] = None,
    ) -> None:
        """Redeems a gift code for the current user."""
        if game is None:
            if self.default_game is None:
                raise RuntimeError("No default game set.")

            game = self.default_game

        if game not in {types.Game.GENSHIN, types.Game.ZZZ, types.Game.STARRAIL, types.Game.TOT}:
            raise ValueError(f"{game} does not support code redemption.")

        uid = uid or await self._get_uid(game)

        try:
            region = region or utility.recognize_server(uid, game)
        except Exception:
            warnings.warn(f"Failed to recognize server for game {game!r} and uid {uid!r}, fetching from API now.")
            region = await self._get_server_region(uid, game)

        await self.request(
            routes.CODE_URL.get_url(self.region, game),
            params=dict(
                uid=uid,
                region=region,
                cdkey=code,
                game_biz=utility.get_prod_game_biz(self.region, game),
                lang=utility.create_short_lang_code(lang or self.lang),
            ),
            method="POST" if game is types.Game.STARRAIL else "GET",
        )

    @managers.no_multi
    async def check_in_community(self) -> None:
        """Check in to the hoyolab community and claim your daily 5 community exp."""
        url = routes.COMMUNITY_URL.get_url(self.region) / "apihub/wapi/mission/signIn"
        await self.request(url, method="POST", data={})
