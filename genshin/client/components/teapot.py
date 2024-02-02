"""Teapot component."""

import functools
import typing

from genshin import paginators, utility
from genshin.client import routes
from genshin.client.components import base
from genshin.models.genshin import teapot as models

__all__ = ["TeapotClient"]


class TeapotClient(base.BaseClient):
    """teapot component."""

    async def request_teapot(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the teapot endpoint."""
        params = dict(params or {})

        base_url = routes.TEAPOT_URL.get_url(self.region)
        url = base_url / endpoint

        params["lang"] = lang or self.lang

        return await self.request(url, method=method, params=params, **kwargs)

    async def _get_teapot_replica_page(
        self,
        page: int,
        *,
        zip_type: int = 1,
        block_id: typing.Optional[str] = None,
        module_id: typing.Optional[str] = None,
        region: typing.Optional[str] = None,
        version: typing.Optional[str] = None,
        limit: int = 20,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.TeapotReplica]:
        """Get a teapot replica page."""
        params = dict(
            next=page * limit,  # weirdest sorting ever
            zip_type=zip_type,
            block_id=block_id or "",
            module_id=module_id or "",
            target_region=region or "",
            version=version or "",
            limit=limit,
        )
        data = await self.request_teapot("list", lang=lang, params=params)
        return [models.TeapotReplica(**entry) for entry in data["articles"]]

    def teapot_replicas(
        self,
        *,
        limit: typing.Optional[int] = None,
        zip_type: int = 1,
        block_id: typing.Optional[str] = None,
        module_id: typing.Optional[str] = None,
        region: typing.Optional[str] = None,
        uid: typing.Optional[int] = None,
        version: typing.Optional[str] = None,
        page_size: int = 20,
        lang: typing.Optional[str] = None,
    ) -> paginators.PagedPaginator[models.TeapotReplica]:
        """Get a teapot replica paginator."""
        if not region and uid:
            region = utility.recognize_genshin_server(uid)

        return paginators.PagedPaginator(
            functools.partial(
                self._get_teapot_replica_page,
                zip_type=zip_type,
                block_id=block_id,
                module_id=module_id,
                region=region,
                version=version,
                limit=page_size,
                lang=lang,
            ),
            limit=limit,
            page_size=page_size,
        )
