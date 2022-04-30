"""Diary component."""
import datetime
import functools
import typing

from genshin import paginators, types, utility
from genshin.client import cache, manager, routes
from genshin.client.components import base
from genshin.models.genshin import diary as models

__all__ = ["DiaryClient"]


class DiaryCallback(typing.Protocol):
    """Callback which requires a diary page."""

    async def __call__(self, page: int, /) -> models.DiaryPage:
        """Return a diary page."""
        ...


class DiaryPaginator(paginators.PagedPaginator[models.DiaryAction]):
    """Paginator for diary."""

    _data: typing.Optional[models.DiaryPage]
    """Metadata of the paginator"""

    def __init__(self, getter: DiaryCallback, *, limit: typing.Optional[int] = None) -> None:
        self._get_page = getter
        self._data = None

        super().__init__(self._getter, limit=limit, page_size=10)

    async def _getter(self, page: int) -> typing.Sequence[models.DiaryAction]:
        self._data = await self._get_page(page)
        return self._data.actions

    @property
    def data(self) -> models.BaseDiary:
        """Get data bound to the diary.

        This requires at least one page to have been fetched.
        """
        if self._data is None:
            raise RuntimeError("At least one item must be fetched before data can be gotten.")

        return self._data


class DiaryClient(base.BaseClient):
    """Diary component."""

    @manager.no_multi
    async def request_ledger(
        self,
        uid: typing.Optional[int] = None,
        *,
        detail: bool = False,
        month: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the ys ledger endpoint."""
        # TODO: Do not separate urls?
        params = dict(params or {})

        url = routes.DETAIL_LEDGER_URL.get_url(self.region) if detail else routes.INFO_LEDGER_URL.get_url(self.region)

        uid = uid or await self._get_uid(types.Game.GENSHIN)
        params["uid"] = uid
        params["region"] = utility.recognize_genshin_server(uid)

        params["month"] = month or datetime.datetime.now().month
        params["lang"] = lang or self.lang

        return await self.request(url, params=params, **kwargs)

    async def get_diary(
        self,
        uid: typing.Optional[int] = None,
        *,
        month: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> models.Diary:
        """Get a traveler's diary with earning details for the month."""
        cache_key = cache.cache_key("diary", month=month or datetime.datetime.now().month, lang=lang or self.lang)
        data = await self.request_ledger(uid, month=month, lang=lang, cache=cache_key)
        return models.Diary(**data)

    async def _get_diary_page(
        self,
        page: int,
        *,
        uid: typing.Optional[int] = None,
        type: int = models.DiaryType.PRIMOGEMS,
        month: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> models.DiaryPage:
        data = await self.request_ledger(
            uid,
            detail=True,
            month=month,
            lang=lang,
            params=dict(type=type, current_page=page, limit=10),
        )
        return models.DiaryPage(**data)

    def diary_log(
        self,
        uid: typing.Optional[int] = None,
        *,
        limit: typing.Optional[int] = None,
        type: int = models.DiaryType.PRIMOGEMS,
        month: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> DiaryPaginator:
        """Create a new daily reward paginator."""
        return DiaryPaginator(
            functools.partial(
                self._get_diary_page,
                uid=uid,
                type=type,
                month=month,
                lang=lang,
            ),
            limit=limit,
        )
