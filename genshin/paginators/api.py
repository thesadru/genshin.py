"""Base paginators made specifically for interaction with the api."""

from __future__ import annotations

import abc
import typing
import warnings

from . import base

if typing.TYPE_CHECKING:
    from genshin import models


__all__ = ["CursorPaginator", "PagedPaginator", "TokenPaginator"]

T = typing.TypeVar("T")
T_co = typing.TypeVar("T_co", covariant=True)
UniqueT = typing.TypeVar("UniqueT", bound="models.Unique")


class GetterCallback(typing.Protocol[T_co]):
    """Callback for returning resources based on a page or cursor."""

    async def __call__(self, page: int, /) -> typing.Sequence[T_co]:
        """Return a sequence of resources."""
        ...


class TokenGetterCallback(typing.Protocol[T_co]):
    """Callback for returning resources based on a page or cursor."""

    async def __call__(self, token: str, /) -> tuple[str, typing.Sequence[T_co]]:
        """Return a sequence of resources."""
        ...


class APIPaginator(typing.Generic[T], base.BufferedPaginator[T], abc.ABC):
    """Paginator for interaction with the api."""

    __slots__ = ("getter",)

    getter: typing.Callable[..., typing.Awaitable[object]]
    """Underlying getter that yields the next page."""


class PagedPaginator(typing.Generic[T], APIPaginator[T]):
    """Paginator for resources which only require a page number.

    Due to ratelimits the requests must be sequential.
    """

    __slots__ = ("_page_size", "current_page")

    getter: GetterCallback[T]
    """Underlying getter that yields the next page."""

    _page_size: typing.Optional[int]
    """Expected non-zero page size to be able to tell the end."""

    current_page: typing.Optional[int]
    """Current page counter.."""

    def __init__(
        self,
        getter: GetterCallback[T],
        *,
        limit: typing.Optional[int] = None,
        page_size: typing.Optional[int] = None,
    ) -> None:
        super().__init__(limit=limit)
        self.getter = getter
        self._page_size = page_size

        self.current_page = 1

    async def next_page(self) -> typing.Optional[typing.Iterable[T]]:
        """Get the next page of the paginator."""
        if self.current_page is None:
            return None

        data = await self.getter(self.current_page)

        if self._page_size is None:
            warnings.warn("No page size specified for resource, having to guess.")
            self._page_size = len(data)

        if len(data) < self._page_size:
            self.current_page = None
            return data

        self.current_page += 1
        return data


class TokenPaginator(typing.Generic[T], APIPaginator[T]):
    """Paginator for resources which require a token."""

    __slots__ = ("_page_size", "token")

    getter: TokenGetterCallback[T]
    """Underlying getter that yields the next page."""

    _page_size: typing.Optional[int]
    """Expected non-zero page size to be able to tell the end."""

    token: typing.Optional[str]

    def __init__(
        self,
        getter: TokenGetterCallback[T],
        *,
        limit: typing.Optional[int] = None,
        page_size: typing.Optional[int] = None,
    ) -> None:
        super().__init__(limit=limit)
        self.getter = getter
        self._page_size = page_size

        self.token = ""

    async def next_page(self) -> typing.Optional[typing.Iterable[T]]:
        """Get the next page of the paginator."""
        if self.token is None:
            return None

        self.token, data = await self.getter(self.token)

        if self._page_size is None:
            warnings.warn("No page size specified for resource, having to guess.")
            self._page_size = len(data)

        if len(data) < self._page_size:
            self.token = None
            return data

        return data


class CursorPaginator(typing.Generic[UniqueT], APIPaginator[UniqueT]):
    """Paginator based on end_id cursors."""

    __slots__ = ("_page_size", "end_id")

    getter: GetterCallback[UniqueT]
    """Underlying getter that yields the next page."""

    _page_size: typing.Optional[int]
    """Expected non-zero page size to be able to tell the end."""

    end_id: typing.Optional[int]
    """Current end id. If none then exhausted."""

    def __init__(
        self,
        getter: GetterCallback[UniqueT],
        *,
        limit: typing.Optional[int] = None,
        end_id: int = 0,
        page_size: typing.Optional[int] = 20,
    ) -> None:
        super().__init__(limit=limit)
        self.getter = getter
        self.end_id = end_id

        self._page_size = page_size

    async def next_page(self) -> typing.Optional[typing.Iterable[UniqueT]]:
        """Get the next page of the paginator."""
        if self.end_id is None:
            return None

        data = await self.getter(self.end_id)

        if self._page_size is None:
            warnings.warn("No page size specified for resource, having to guess.")
            self._page_size = len(data)

        if len(data) < self._page_size:
            self.end_id = None
            return data

        self.end_id = data[-1].id
        return data
