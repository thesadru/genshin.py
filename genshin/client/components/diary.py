"""Diary component."""

import datetime
import functools
import typing

from genshin import paginators, types, utility
from genshin.client import cache, routes
from genshin.client.components import base
from genshin.client.manager import managers
from genshin.constants import CN_TIMEZONE
from genshin.models.genshin import diary as models
from genshin.utility import deprecation

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

        super().__init__(self._getter, limit=limit, page_size=100)

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


class StarRailDiaryCallback(typing.Protocol):
    """Callback which requires a diary page."""

    async def __call__(self, page: int, /) -> models.StarRailDiaryPage:
        """Return a diary page."""
        ...


class StarRailDiaryPaginator(paginators.PagedPaginator[models.StarRailDiaryAction]):
    """Paginator for diary."""

    _data: typing.Optional[models.StarRailDiaryPage]
    """Metadata of the paginator"""

    def __init__(self, getter: StarRailDiaryCallback, *, limit: typing.Optional[int] = None) -> None:
        self._get_page = getter
        self._data = None

        super().__init__(self._getter, limit=limit, page_size=100)

    async def _getter(self, page: int) -> typing.Sequence[models.StarRailDiaryAction]:
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

    @managers.no_multi
    async def request_ledger(
        self,
        uid: typing.Optional[int] = None,
        *,
        game: typing.Optional[types.Game] = None,
        detail: bool = False,
        month: typing.Union[int, str, None] = None,
        lang: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the ys ledger endpoint."""
        # TODO: Do not separate urls?
        params = dict(params or {})

        if game is None:
            if self.default_game is None:
                raise RuntimeError("No default game set.")

            game = self.default_game

        base_url = routes.DETAIL_LEDGER_URL if detail else routes.INFO_LEDGER_URL
        url = base_url.get_url(self.region, game)

        uid = uid or await self._get_uid(game)

        if self.region == types.Region.OVERSEAS or game == types.Game.STARRAIL:
            params["uid"] = uid
            params["region"] = utility.recognize_server(uid, game)
        elif self.region == types.Region.CHINESE:
            params["bind_uid"] = uid
            params["bind_region"] = utility.recognize_server(uid, game)
        else:
            raise TypeError(f"{self.region!r} is not a valid region.")
        params["month"] = month or (
            datetime.datetime.now().strftime("%Y%m") if game == types.Game.STARRAIL else datetime.datetime.now().month
        )
        params["lang"] = lang or self.lang

        return await self.request(url, params=params, **kwargs)

    @deprecation.deprecated("get_genshin_diary")
    async def get_diary(
        self,
        uid: typing.Optional[int] = None,
        *,
        month: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> models.Diary:
        """Get a traveler's diary with earning details for the month."""
        return await self.get_genshin_diary(uid, month=month, lang=lang)

    async def get_genshin_diary(
        self,
        uid: typing.Optional[int] = None,
        *,
        month: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> models.Diary:
        """Get a traveler's diary with earning details for the month."""
        game = types.Game.GENSHIN
        uid = uid or await self._get_uid(game)
        cache_key = cache.cache_key(
            "diary", uid=uid, game=game, month=month or datetime.datetime.now(CN_TIMEZONE).month, lang=lang or self.lang
        )
        data = await self.request_ledger(uid, game=game, month=month, lang=lang, cache=cache_key)
        return models.Diary(**data)

    async def get_starrail_diary(
        self,
        uid: typing.Optional[int] = None,
        *,
        month: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> models.StarRailDiary:
        """Get a blazer's diary with earning details for the month."""
        game = types.Game.STARRAIL
        uid = uid or await self._get_uid(game)
        cache_key = cache.cache_key(
            "diary", uid=uid, game=game, month=month or datetime.datetime.now(CN_TIMEZONE).month, lang=lang or self.lang
        )
        data = await self.request_ledger(uid, game=game, month=month, lang=lang, cache=cache_key)
        return models.StarRailDiary(**data)

    async def _get_genshin_diary_page(
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
            game=types.Game.GENSHIN,
            detail=True,
            month=month,
            lang=lang,
            params=dict(type=type, current_page=page, page_size=100),
        )
        return models.DiaryPage(**data)

    @deprecation.deprecated("genshin_diary_log")
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
        return self.genshin_diary_log(
            uid=uid,
            limit=limit,
            type=type,
            month=month,
            lang=lang,
        )

    def genshin_diary_log(
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
                self._get_genshin_diary_page,
                uid=uid,
                type=type,
                month=month,
                lang=lang,
            ),
            limit=limit,
        )

    async def _get_starrail_diary_page(
        self,
        page: int,
        *,
        uid: typing.Optional[int] = None,
        type: int = models.StarRailDiaryType.STELLARJADE,
        month: typing.Optional[str] = None,
        lang: typing.Optional[str] = None,
    ) -> models.StarRailDiaryPage:
        data = await self.request_ledger(
            uid,
            game=types.Game.STARRAIL,
            detail=True,
            month=month,
            lang=lang,
            params=dict(type=type, current_page=page, page_size=100),
        )
        return models.StarRailDiaryPage(**data)

    def starrail_diary_log(
        self,
        uid: typing.Optional[int] = None,
        *,
        limit: typing.Optional[int] = None,
        type: int = models.StarRailDiaryType.STELLARJADE,
        month: typing.Optional[str] = None,
        lang: typing.Optional[str] = None,
    ) -> StarRailDiaryPaginator:
        """Create a new daily reward paginator."""
        return StarRailDiaryPaginator(
            functools.partial(
                self._get_starrail_diary_page,
                uid=uid,
                type=type,
                month=month,
                lang=lang,
            ),
            limit=limit,
        )
