"""Base paginators made specifically for interaction with the api."""
from __future__ import annotations

import abc
import typing

from . import base

if typing.TYPE_CHECKING:
    from genshin import models


__all__ = ["CursorPaginator", "PagedPaginator"]

T = typing.TypeVar("T")
UniqueT = typing.TypeVar("UniqueT", bound="models.Unique")
GetterCallback = typing.Callable[..., typing.Awaitable[typing.Sequence[T]]]
# in reality ((int) -> Awaitable[Sequence[T]]) but mypy is being dumb


class APIPaginator(typing.Generic[T], base.BufferedPaginator[T], abc.ABC):
    """Paginator for interaction with the api."""


class PagedPaginator(typing.Generic[T], APIPaginator[T]):
    """Paginator for resources which only require a page number."""

    _getter: GetterCallback[T]
    _page_size: typing.Optional[int]
    current_page: typing.Optional[int]

    def __init__(
        self,
        getter: GetterCallback[T],
        *,
        limit: typing.Optional[int] = None,
        page_size: typing.Optional[int] = None,
    ) -> None:
        super().__init__(limit=limit)
        self._getter = getter  # type: ignore [assignment]
        self._page_size = page_size
        self.current_page = 1

    async def next_page(self) -> typing.Optional[typing.Iterable[T]]:
        """Get the next page of the paginator."""
        if self.current_page is None:
            return None

        data = await self._getter(self.current_page)

        if self._page_size is None:
            self._page_size = len(data)

        if len(data) < self._page_size:
            self.current_page = None
            return data

        self.current_page += 1
        return data


class CursorPaginator(typing.Generic[UniqueT], APIPaginator[UniqueT]):
    """Paginator based on end_id cursors."""

    _end_id: typing.Optional[int]

    _getter: GetterCallback[UniqueT]
    _page_size: int = 20

    def __init__(
        self,
        getter: GetterCallback[UniqueT],
        *,
        limit: typing.Optional[int] = None,
        end_id: int = 0,
    ) -> None:
        super().__init__(limit=limit)
        self._getter = getter  # type: ignore [assignment]
        self._end_id = end_id

    async def next_page(self) -> typing.Optional[typing.Iterable[UniqueT]]:
        """Get the next page of the paginator."""
        if self._end_id is None:
            raise Exception("No more pages")

        data = await self._getter(self._end_id)

        if self._page_size is None:
            self._page_size = len(data)

        if len(data) < self._page_size:
            self.end_id = None
            return data

        self._end_id = data[-1].id
        return data
