"""Wish component."""

import asyncio
import functools
import typing
import urllib.parse

import aiohttp

from genshin import paginators
from genshin.client import routes
from genshin.client.components import base
from genshin.models.genshin import wish as models
from genshin.utility import genshin as genshin_utility

__all__ = ["WishClient"]


class WishClient(base.BaseClient):
    """Wish component."""

    async def request_gacha_info(
        self,
        endpoint: str,
        *,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the gacha info endpoint."""
        params = dict(params or {})
        authkey = authkey or self.authkey

        if authkey is None:
            raise RuntimeError("No authkey provided")

        base_url = routes.GACHA_INFO_URL.get_url(self.region)
        url = base_url / endpoint

        params["authkey_ver"] = 1
        params["authkey"] = urllib.parse.unquote(authkey)
        params["lang"] = genshin_utility.create_short_lang_code(lang or self.lang)

        return await self.request(url, params=params, **kwargs)

    async def _get_wish_page(
        self,
        end_id: int,
        banner_type: int,
        *,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
    ) -> typing.Sequence[models.Wish]:
        """Get a single page of wishes."""
        data = await self.request_gacha_info(
            "getGachaLog",
            lang=lang,
            authkey=authkey,
            params=dict(gacha_type=banner_type, size=20, end_id=end_id),
        )

        banner_names = await self.get_banner_names(lang=lang, authkey=authkey)

        return [models.Wish(**i, banner_name=banner_names[banner_type]) for i in data["list"]]

    def wish_history(
        self,
        banner_type: typing.Union[int, typing.Sequence[int], None] = None,
        *,
        limit: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
        end_id: int = 0,
    ) -> paginators.Paginator[models.Wish]:
        """Get the wish history of a user."""
        banner_types = banner_type or [100, 200, 301, 302]

        if not isinstance(banner_types, typing.Sequence):
            banner_types = [banner_types]

        iterators: typing.List[paginators.Paginator[models.Wish]] = []
        for banner in banner_types:
            iterators.append(
                paginators.CursorPaginator(
                    functools.partial(
                        self._get_wish_page,
                        banner_type=banner,
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

    async def get_banner_names(
        self,
        *,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
    ) -> typing.Mapping[int, str]:
        """Get a list of banner names."""
        data = await self.request_gacha_info(
            "getConfigList",
            lang=lang,
            authkey=authkey,
        )
        return {typing.cast("models.BannerType", int(i["key"])): i["name"] for i in data["gacha_type_list"]}

    async def _get_banner_details(
        self,
        banner_id: str,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.BannerDetails:
        """Get details of a specific banner using its id."""
        data = await self.request_webstatic(f"/hk4e/gacha_info/os_asia/{banner_id}/{lang or self.lang}.json")
        return models.BannerDetails(**data, banner_id=banner_id)

    async def get_banner_details(
        self,
        banner_ids: typing.Optional[typing.Sequence[str]] = None,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.BannerDetails]:
        """Get all banner details at once in a batch."""
        if not banner_ids:
            try:
                banner_ids = genshin_utility.get_banner_ids()
            except FileNotFoundError:
                banner_ids = []

            if len(banner_ids) < 3:
                banner_ids = await self.fetch_banner_ids()

        data = await asyncio.gather(*(self._get_banner_details(i, lang=lang) for i in banner_ids))
        return list(data)

    async def get_gacha_items(
        self,
        *,
        server: str = "os_asia",
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.GachaItem]:
        """Get the list of characters and weapons that can be gotten from the gacha."""
        data = await self.request_webstatic(f"/hk4e/gacha_info/{server}/items/{lang or self.lang}.json")
        return [models.GachaItem(**i) for i in data]

    async def fetch_banner_ids(self) -> typing.Sequence[str]:
        """Fetch banner ids from a user-mantained github repository."""
        url = "https://raw.githubusercontent.com/thesadru/genshindata/master/banner_ids.txt"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                data = await r.text()

        return data.splitlines()
