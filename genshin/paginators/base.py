"""Base paginators."""

from __future__ import annotations

import abc
import asyncio
import heapq
import typing

__all__ = ["BufferedPaginator", "MergedPaginator", "Paginator"]

T = typing.TypeVar("T")

sentinel: typing.Any = object()


async def _try_gather_first(iterators: typing.Iterable[typing.AsyncIterator[T]]) -> typing.Sequence[T]:
    """Gather all the first values of iterators at once."""
    coros = (it.__anext__() for it in iterators)
    gathered = await asyncio.gather(*coros, return_exceptions=True)

    values: typing.List[T] = []
    for x in gathered:
        if isinstance(x, BaseException):
            if not isinstance(x, StopAsyncIteration):
                raise x from None
            else:
                values.append(sentinel)
        else:
            values.append(x)

    return values


async def flatten(iterable: typing.AsyncIterable[T]) -> typing.Sequence[T]:
    """Flatten an async iterable."""
    if isinstance(iterable, Paginator):
        return await iterable.flatten()

    return [x async for x in iterable]


async def aiterate(iterable: typing.Iterable[T]) -> typing.AsyncIterator[T]:
    """Turn a plain iterable into an async iterator."""
    for i in iterable:
        yield i


class Paginator(typing.Generic[T], abc.ABC):
    """Base paginator."""

    async def next(self) -> T:
        """Return the next element."""
        try:
            return await self.__anext__()
        except StopAsyncIteration:
            raise LookupError("No elements were found") from None

    def _complete(self) -> typing.NoReturn:
        raise StopAsyncIteration("No more items exist in this paginator. It has been exhausted.") from None

    def __aiter__(self) -> Paginator[T]:
        return self

    async def flatten(self) -> typing.Sequence[T]:
        """Flatten the paginator."""
        return [item async for item in self]

    def __await__(self) -> typing.Generator[None, None, typing.Sequence[T]]:
        return self.flatten().__await__()

    @abc.abstractmethod
    async def __anext__(self) -> T:
        ...


class BasicPaginator(typing.Generic[T], Paginator[T], abc.ABC):
    """Paginator that simply iterates over an iterable."""

    iterator: typing.AsyncIterator[T]
    """Underlying iterator."""

    def __init__(self, iterable: typing.Union[typing.Iterable[T], typing.AsyncIterable[T]]) -> None:
        if isinstance(iterable, typing.AsyncIterable):
            self.iterator = iterable.__aiter__()
        else:
            self.iterator = aiterate(iterable)

    async def __anext__(self) -> T:
        try:
            return await self.iterator.__anext__()
        except StopAsyncIteration:
            self._complete()


class BufferedPaginator(typing.Generic[T], Paginator[T], abc.ABC):
    """Paginator with a support for buffers."""

    limit: typing.Optional[int] = None
    """Limit of items to be yielded."""

    _buffer: typing.Optional[typing.Iterator[T]]
    """Item buffer. If none then exhausted."""

    _counter: int
    """Amount of yielded items so far. No guarantee to be synchronized."""

    def __init__(self, *, limit: typing.Optional[int] = None) -> None:
        self.limit = limit
        self._buffer = iter(())
        self._counter = 0

    @property
    def exhausted(self) -> bool:
        """Whether all pages have been fetched."""
        return self._buffer is None

    def _complete(self) -> typing.NoReturn:
        self._buffer = None

        super()._complete()
        raise  # pyright bug

    @abc.abstractmethod
    async def next_page(self) -> typing.Optional[typing.Iterable[T]]:
        """Get the next page of the paginator."""

    async def __anext__(self) -> T:
        if not self._buffer:
            self._complete()

        if self.limit and self._counter >= self.limit:
            self._complete()

        self._counter += 1

        try:
            return next(self._buffer)
        except StopIteration:
            pass

        buffer = await self.next_page()
        if not buffer:
            self._complete()

        self._buffer = iter(buffer)
        return next(self._buffer)


class MergedPaginator(typing.Generic[T], Paginator[T]):
    """A paginator merging a collection of iterators."""

    heap: typing.List[typing.Tuple[typing.Any, int, T, typing.AsyncIterator[T]]]
    """Underlying heap queue."""

    _iterators: typing.Sequence[typing.AsyncIterator[T]]
    """Entry iterators.

    Only used as pointers to a heap.
    """

    limit: typing.Optional[int] = None
    """Limit of items to be yielded"""

    _key: typing.Optional[typing.Callable[[T], typing.Any]]
    """Sorting key."""

    _prepared: bool = False
    """Whether the paginator is prepared"""

    _counter: int
    """Amount of yielded items so far. No guarantee to be synchronized."""

    def __init__(
        self,
        iterables: typing.Sequence[typing.AsyncIterable[T]],
        *,
        key: typing.Optional[typing.Callable[[T], typing.Any]] = None,
        limit: typing.Optional[int] = None,
    ) -> None:
        self._iterators = [iterable.__aiter__() for iterable in iterables]
        # TODO: Handle optional keys decently enough for mypy to pass
        self._key = key
        self.limit = limit

        self._prepared = False
        self._counter = 0

    def _complete(self) -> typing.NoReturn:
        self.heap = []
        self._iterators = []

        super()._complete()
        raise  # pyright bug

    async def _prepare(self) -> None:
        # TODO: Move _try_gather_first together
        first_values = await _try_gather_first(self._iterators)

        self.heap = [
            (self._key(value) if self._key else value, order, value, it)
            for order, (it, value) in enumerate(zip(self._iterators, first_values))
            if value is not sentinel
        ]
        heapq.heapify(self.heap)

        self._prepared = True

    async def __anext__(self) -> T:
        if not self._prepared:
            await self._prepare()

        if not self.heap:
            self._complete()

        if self.limit and self._counter >= self.limit:
            self._complete()

        self._counter += 1

        _, order, value, it = self.heap[0]

        try:
            new_value = await it.__anext__()
        except StopAsyncIteration:
            heapq.heappop(self.heap)
            return value

        heapq.heapreplace(self.heap, (self._key(new_value) if self._key else new_value, order, new_value, it))

        return value

    async def flatten(self, *, lazy: bool = False) -> typing.Sequence[T]:
        """Flatten the paginator."""
        if self.limit is not None and lazy:
            return [item async for item in self]

        coros = (flatten(i) for i in self._iterators)
        lists = await asyncio.gather(*coros)

        return list(heapq.merge(*lists, key=self._key))[: self.limit]
