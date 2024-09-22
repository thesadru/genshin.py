"""Wish component."""

import asyncio
import functools
import typing
import urllib.parse
import warnings

from genshin import paginators, types, utility
from genshin.client import cache as client_cache
from genshin.client import routes
from genshin.client.components import base
from genshin.models.genshin import gacha as models
from genshin.utility import deprecation

__all__ = ["WishClient"]


class WishClient(base.BaseClient):
    """Wish component."""

    async def request_gacha_info(
        self,
        endpoint: str,
        *,
        lang: typing.Optional[str] = None,
        game: typing.Optional[types.Game] = None,
        authkey: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the gacha info endpoint."""
        params = dict(params or {})
        game = game or self.default_game
        if game is None:
            raise RuntimeError("No game provided")

        authkey = authkey or self.authkeys.get(game)
        if authkey is None:
            raise RuntimeError("No authkey provided")

        base_url = routes.GACHA_URL.get_url(self.region, game)
        url = base_url / endpoint

        params["authkey_ver"] = 1
        params["authkey"] = urllib.parse.unquote(authkey)
        params["lang"] = utility.create_short_lang_code(lang or self.lang)
        params["game_biz"] = utility.get_prod_game_biz(self.region, game)

        return await self.request(url, params=params, **kwargs)

    async def _get_gacha_page(
        self,
        end_id: int,
        banner_type: int,
        *,
        game: typing.Optional[types.Game] = None,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
    ) -> tuple[typing.Sequence[typing.Any], int]:
        """Get a single page of wishes."""
        data = await self.request_gacha_info(
            "getGachaLog",
            lang=lang,
            game=game,
            authkey=authkey,
            params=dict(gacha_type=banner_type, real_gacha_type=banner_type, size=20, end_id=end_id),
        )

        if game is types.Game.GENSHIN:
            # Genshin doesn't return timezone data
            # America: UTC-5, Europe: UTC+1, others are UTC+8
            tz_offsets = {"os_usa": -13, "os_euro": -7}
            tz_offset = tz_offsets.get(data["region"], 0)
        else:
            tz_offset = data["region_time_zone"]
            if game is types.Game.STARRAIL:
                tz_offset -= 8  # Star rail returns UTC+n for this value

        return data["list"], tz_offset

    async def _get_wish_page(
        self,
        end_id: int,
        banner_type: models.GenshinBannerType,
        *,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
    ) -> typing.Sequence[models.Wish]:
        """Get a single page of wishes."""
        data, tz_offset = await self._get_gacha_page(
            end_id=end_id,
            banner_type=banner_type,
            lang=lang,
            authkey=authkey,
            game=types.Game.GENSHIN,
        )
        return [models.Wish(**i, banner_type=banner_type, tz_offset=tz_offset) for i in data]

    async def _get_warp_page(
        self,
        end_id: int,
        banner_type: models.StarRailBannerType,
        *,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
    ) -> typing.Sequence[models.Warp]:
        """Get a single page of warps."""
        data, tz_offset = await self._get_gacha_page(
            end_id=end_id,
            banner_type=banner_type,
            lang=lang,
            authkey=authkey,
            game=types.Game.STARRAIL,
        )

        return [models.Warp(**i, banner_type=banner_type, tz_offset=tz_offset) for i in data]

    async def _get_signal_page(
        self,
        end_id: int,
        banner_type: models.ZZZBannerType,
        *,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
    ) -> typing.Sequence[models.SignalSearch]:
        """Get a single page of warps."""
        data, tz_offset = await self._get_gacha_page(
            end_id=end_id,
            banner_type=banner_type,
            lang=lang,
            authkey=authkey,
            game=types.Game.ZZZ,
        )

        return [models.SignalSearch(**i, banner_type=banner_type, tz_offset=tz_offset) for i in data]

    def wish_history(
        self,
        banner_type: typing.Optional[typing.Union[int, typing.Sequence[int]]] = None,
        *,
        limit: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
        end_id: int = 0,
    ) -> paginators.Paginator[models.Wish]:
        """Get the wish history of a user."""
        banner_types = banner_type or [100, 200, 301, 302, 500]

        if not isinstance(banner_types, typing.Sequence):
            banner_types = [banner_types]

        iterators: list[paginators.Paginator[models.Wish]] = []
        for banner in banner_types:
            iterators.append(
                paginators.CursorPaginator(
                    functools.partial(
                        self._get_wish_page,
                        banner_type=typing.cast(models.GenshinBannerType, banner),
                        lang=lang,
                        authkey=authkey,
                    ),
                    limit=limit,
                    end_id=end_id,
                )
            )

        if len(iterators) == 1:
            return iterators[0]

        return paginators.MergedPaginator(iterators, key=lambda wish: wish.time.timestamp())

    def warp_history(
        self,
        banner_type: typing.Optional[typing.Union[int, typing.Sequence[int]]] = None,
        *,
        limit: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
        end_id: int = 0,
    ) -> paginators.Paginator[models.Warp]:
        """Get the warp history of a user."""
        banner_types = banner_type or [1, 2, 11, 12]

        if not isinstance(banner_types, typing.Sequence):
            banner_types = [banner_types]

        iterators: list[paginators.Paginator[models.Warp]] = []
        for banner in banner_types:
            iterators.append(
                paginators.CursorPaginator(
                    functools.partial(
                        self._get_warp_page,
                        banner_type=typing.cast(models.StarRailBannerType, banner),
                        lang=lang,
                        authkey=authkey,
                    ),
                    limit=limit,
                    end_id=end_id,
                )
            )

        if len(iterators) == 1:
            return iterators[0]

        return paginators.MergedPaginator(iterators, key=lambda wish: wish.time.timestamp())

    def signal_history(
        self,
        banner_type: typing.Optional[typing.Union[int, typing.Sequence[int]]] = None,
        *,
        limit: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
        end_id: int = 0,
    ) -> paginators.Paginator[models.SignalSearch]:
        """Get the signal search history of a user."""
        banner_types = banner_type or [1, 2, 3, 5]

        if not isinstance(banner_types, typing.Sequence):
            banner_types = [banner_types]

        iterators: list[paginators.Paginator[models.SignalSearch]] = []
        for banner in banner_types:
            iterators.append(
                paginators.CursorPaginator(
                    functools.partial(
                        self._get_signal_page,
                        banner_type=typing.cast(models.ZZZBannerType, banner),
                        lang=lang,
                        authkey=authkey,
                    ),
                    limit=limit,
                    end_id=end_id,
                )
            )

        if len(iterators) == 1:
            return iterators[0]

        return paginators.MergedPaginator(iterators, key=lambda wish: wish.time.timestamp())

    @deprecation.deprecated("get_genshin_banner_names")
    async def get_banner_names(
        self,
        *,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
    ) -> typing.Mapping[int, str]:
        """Get a list of banner names."""
        return await self.get_genshin_banner_names(lang=lang, authkey=authkey)

    async def get_genshin_banner_names(
        self,
        *,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
    ) -> typing.Mapping[int, str]:
        """Get a list of banner names."""
        data = await self.request_gacha_info(
            "getConfigList",
            lang=lang,
            game=types.Game.GENSHIN,
            authkey=authkey,
            static_cache=client_cache.cache_key("banner", endpoint="names", lang=lang or self.lang),
        )
        return {int(i["key"]): i["name"] for i in data["gacha_type_list"]}

    async def _get_banner_details(
        self,
        banner_id: str,
        *,
        game: typing.Optional[types.Game] = None,
        lang: typing.Optional[str] = None,
    ) -> models.BannerDetails:
        """Get details of a specific banner using its id."""
        lang = lang or self.lang
        game = game or self.default_game
        if game is None:
            raise RuntimeError("No game provided")
        if game == types.Game.STARRAIL:
            warnings.warn("Banner details for Star Rail are not fully supported.")

        region = "hkrpg" if game == types.Game.STARRAIL else "hk4e"
        server = "prod_official_asia" if game == types.Game.STARRAIL else "os_asia"

        data = await self.request_webstatic(
            f"/gacha_info/{region}/{server}/{banner_id}/{lang}.json",
            cache=client_cache.cache_key("banner", endpoint="details", banner=banner_id, lang=lang),
        )
        return models.BannerDetails(**data, banner_id=banner_id)

    @deprecation.deprecated("get_genshin_banner_ids")
    async def get_banner_ids(self) -> typing.Sequence[str]:
        """Get a list of banner ids.

        Uses the current cn banners.
        """
        return await self.get_genshin_banner_ids()

    async def get_genshin_banner_ids(self) -> typing.Sequence[str]:
        """Get a list of banner ids.

        Uses the current cn banners.
        """

        def process_gacha(data: typing.Mapping[str, typing.Any]) -> str:
            # Temporary fix for 4.5 chronicled wish
            if data["gacha_type"] == 500:
                return "8b10b48c52dd6870f92d72e9963b44bb8968ed2f"
            return data["gacha_id"]

        data = await self.request_webstatic(
            "gacha_info/hk4e/cn_gf01/gacha/list.json",
            region=types.Region.CHINESE,
            cache=client_cache.cache_key("banner", endpoint="ids"),
        )
        return list(map(process_gacha, data["data"]["list"]))

    async def get_banner_details(
        self,
        banner_ids: typing.Optional[typing.Sequence[str]] = None,
        *,
        game: typing.Optional[types.Game] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.BannerDetails]:
        """Get all banner details at once in a batch."""
        game = game or self.default_game
        if game == types.Game.STARRAIL and not banner_ids:
            raise RuntimeError("No banner ids provided for star rail")

        banner_ids = banner_ids or await self.get_genshin_banner_ids()

        coros = (self._get_banner_details(i, lang=lang, game=game) for i in banner_ids)
        data = await asyncio.gather(*coros)
        return list(data)

    @deprecation.deprecated("get_genshin_gacha_items")
    async def get_gacha_items(
        self,
        *,
        server: str = "os_asia",
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.GachaItem]:
        """Get the list of characters and weapons that can be gotten from the gacha."""
        return await self.get_genshin_gacha_items(server=server, lang=lang)

    async def get_genshin_gacha_items(
        self,
        *,
        server: str = "os_asia",
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.GachaItem]:
        """Get the list of characters and weapons that can be gotten from the gacha."""
        raise RuntimeError("This method is currently broken, if you know how to fix it, please open an issue.")
        lang = lang or self.lang
        data = await self.request_webstatic(
            f"/hk4e/gacha_info/{server}/items/{lang}.json",
            cache=client_cache.cache_key("banner", endpoint="items", lang=lang),
        )
        return [models.GachaItem(**i) for i in data]
