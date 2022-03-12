"""Base paginators."""

from __future__ import annotations

import abc
import asyncio
import heapq
import typing

__all__ = ["BufferedPaginator", "MergedPaginator", "Paginator"]

T = typing.TypeVar("T")


async def _try_gather_first(iterators: typing.Iterable[typing.AsyncIterator[T]]) -> typing.Sequence[T]:
    """Gather all the first values of iterators at once."""
    __tracebackhide__ = True  # for pytest

    coros = (it.__anext__() for it in iterators)
    gathered = await asyncio.gather(*coros, return_exceptions=True)

    values: typing.List[T] = []
    for x in gathered:
        if isinstance(x, BaseException):
            if not isinstance(x, StopAsyncIteration):
                raise x from None
        else:
            values.append(x)

    return values


async def amerge(
    iterables: typing.Iterable[typing.AsyncIterable[T]],
    key: typing.Optional[typing.Callable[[T], typing.Any]] = None,
    limit: typing.Optional[int] = None,
) -> typing.AsyncIterator[T]:
    """heapq.merge for async iterators."""
    key = key or (lambda x: x)

    iterators = [i.__aiter__() for i in iterables]
    values = await _try_gather_first(iterators)

    heap: typing.List[typing.List[typing.Any]] = [
        [key(value), order, value, it.__anext__] for order, (it, value) in enumerate(zip(iterators, values))
    ]

    heapq.heapify(heap)

    counter = 0

    while heap:
        try:
            while True:
                _, _, value, anext = s = heap[0]

                counter += 1
                if limit and counter > limit:
                    return

                yield value
                value = await anext()
                s[0] = key(value)
                s[2] = value
                heapq.heapreplace(heap, s)
        except StopAsyncIteration:
            heapq.heappop(heap)


async def flatten(iterable: typing.AsyncIterable[T]) -> typing.Sequence[T]:
    """Flatten an async iterable."""
    return [x async for x in iterable]


class Paginator(typing.Generic[T], abc.ABC):
    """Base paginator."""

    async def next(self) -> T:
        """Return the next element."""
        try:
            return await self.__anext__()
        except StopAsyncIteration:
            raise LookupError("No elements were found") from None

    def _complete(self) -> typing.NoReturn:
        raise StopAsyncIteration("No more items exist in this iterator. It has been exhausted.") from None

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


class BufferedPaginator(typing.Generic[T], Paginator[T], abc.ABC):
    """Paginator with a support for buffers."""

    limit: typing.Optional[int] = None
    """Limit of items to be yielded."""

    _buffer: typing.Optional[typing.Iterator[T]]
    """Item buffer. If none then exhausted."""

    counter: int
    """Amount of yielded items so far."""

    def __init__(self, *, limit: typing.Optional[int] = None) -> None:
        self.limit = limit
        self._buffer = iter(())
        self.counter = 0

    @property
    def exhausted(self) -> bool:
        """Whether all pages have been fetched."""
        return self._buffer is None

    @abc.abstractmethod
    async def next_page(self) -> typing.Optional[typing.Iterable[T]]:
        """Get the next page of the paginator."""

    async def __anext__(self) -> T:
        if not self._buffer:
            self._complete()

        self.counter += 1
        if self.limit and self.counter > self.limit:
            self._complete()

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

    limit: typing.Optional[int]
    _iterators: typing.Sequence[typing.AsyncIterator[T]]

    def __init__(
        self,
        iterators: typing.Sequence[typing.AsyncIterator[T]],
        *,
        key: typing.Optional[typing.Callable[[T], typing.Any]] = None,
        limit: typing.Optional[int] = None,
    ) -> None:
        self.limit = limit

        self._iterators = iterators
        self._key = key

        # TODO: get rid of amerge?
        self._merged = amerge(self._iterators, key=self._key, limit=self.limit)

    async def __anext__(self) -> T:
        return await self._merged.__anext__()

    async def flatten(self, *, lazy: bool = False) -> typing.Sequence[T]:
        """Flatten the paginator."""
        if self.limit is not None and lazy:
            return await super().flatten()

        coros = (flatten(i) for i in self._iterators)
        lists = await asyncio.gather(*coros)

        return list(heapq.merge(*lists, key=self._key))[: self.limit]
