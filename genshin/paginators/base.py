"""Base paginators."""

from __future__ import annotations

import abc
import asyncio
import heapq
import random
import typing

__all__ = ["BufferedPaginator", "MergedPaginator", "Paginator"]

T = typing.TypeVar("T")


async def flatten(iterable: typing.AsyncIterable[T]) -> typing.Sequence[T]:
    """Flatten an async iterable."""
    if isinstance(iterable, Paginator):
        return await iterable.flatten()  # type: ignore

    return [x async for x in iterable]


async def aiterate(iterable: typing.Iterable[T]) -> typing.AsyncIterator[T]:
    """Turn a plain iterable into an async iterator."""
    for i in iterable:
        yield i


class Paginator(typing.Generic[T], abc.ABC):
    """Base paginator."""

    __slots__ = ()

    @property
    def _repr_attributes(self) -> typing.Sequence[str]:
        """Attributes to be used in repr."""
        return [
            attribute
            for subclass in self.__class__.__mro__
            for attribute in getattr(subclass, "__slots__", ())
            if not attribute.startswith("_")
        ]

    def __repr__(self) -> str:
        kwargs = ", ".join(f"{name}={getattr(self, name, 'undefined')!r}" for name in self._repr_attributes)
        return f"{self.__class__.__name__}({kwargs})"

    def __pretty__(
        self,
        fmt: typing.Callable[[typing.Any], str],
        **kwargs: typing.Any,
    ) -> typing.Iterator[typing.Any]:
        """Devtools pretty formatting."""
        yield self.__class__.__name__
        yield "("
        yield 1

        for name in self._repr_attributes:
            yield name
            yield "="
            if hasattr(self, name):
                yield fmt(getattr(self, name))
            else:
                yield "<undefined>"

            yield 0

        yield -1
        yield ")"

    async def next(self) -> T:
        """Return the next element."""
        try:
            return await self.__anext__()
        except StopAsyncIteration:
            raise LookupError("No elements were found") from None

    def _complete(self) -> typing.NoReturn:
        """Mark paginator as complete and clear memory."""
        raise StopAsyncIteration("No more items exist in this paginator. It has been exhausted.") from None

    def __aiter__(self) -> Paginator[T]:
        return self

    async def flatten(self) -> typing.Sequence[T]:
        """Flatten the paginator."""
        return [item async for item in self]

    def __await__(self) -> typing.Generator[None, None, typing.Sequence[T]]:
        return self.flatten().__await__()

    @abc.abstractmethod
    async def __anext__(self) -> T: ...


class BasicPaginator(typing.Generic[T], Paginator[T], abc.ABC):
    """Paginator that simply iterates over an iterable."""

    __slots__ = ("iterator",)

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

    __slots__ = ("limit", "_buffer", "_counter")

    limit: typing.Optional[int]
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

    __slots__ = ("iterators", "_heap", "limit", "_key", "_prepared", "_counter")

    # TODO: Use named tuples for the heap

    iterators: typing.Sequence[typing.AsyncIterator[T]]
    """Entry iterators.

    Only used as pointers to a heap.
    """

    _heap: list[tuple[typing.Any, int, T, typing.AsyncIterator[T]]]
    """Underlying heap queue.

    List of (comparable, unique order id, value, iterator)
    """

    limit: typing.Optional[int]
    """Limit of items to be yielded"""

    _key: typing.Optional[typing.Callable[[T], typing.Any]]
    """Sorting key."""

    _prepared: bool
    """Whether the paginator is prepared"""

    _counter: int
    """Amount of yielded items so far. No guarantee to be synchronized."""

    def __init__(
        self,
        iterables: typing.Collection[typing.AsyncIterable[T]],
        *,
        key: typing.Optional[typing.Callable[[T], typing.Any]] = None,
        limit: typing.Optional[int] = None,
    ) -> None:
        self.iterators = [iterable.__aiter__() for iterable in iterables]
        self._key = key
        self.limit = limit

        self._prepared = False
        self._counter = 0

    def _complete(self) -> typing.NoReturn:
        """Mark paginator as complete and clear memory."""
        # free memory in heaps
        self._heap = []
        self.iterators = []

        super()._complete()
        raise  # pyright bug

    def _create_heap_item(
        self,
        value: T,
        iterator: typing.AsyncIterator[T],
        order: typing.Optional[int] = None,
    ) -> tuple[typing.Any, int, T, typing.AsyncIterator[T]]:
        """Create a new item for the heap queue."""
        sort_value = self._key(value) if self._key else value
        if order is None:
            order = random.getrandbits(16)

        return (sort_value, order, value, iterator)

    async def _prepare(self) -> None:
        """Prepare the heap queue by filling it with initial values."""
        coros = (it.__anext__() for it in self.iterators)
        first_values = await asyncio.gather(*coros, return_exceptions=True)

        self._heap = []
        for order, (it, value) in enumerate(zip(self.iterators, first_values)):
            if isinstance(value, BaseException):
                if isinstance(value, StopAsyncIteration):
                    continue

                raise value

            heapq.heappush(self._heap, self._create_heap_item(value, iterator=it, order=order))

        self._prepared = True

    async def __anext__(self) -> T:
        if not self._prepared:
            await self._prepare()

        if not self._heap:
            self._complete()

        if self.limit and self._counter >= self.limit:
            self._complete()

        self._counter += 1

        _, order, value, it = self._heap[0]

        try:
            new_value = await it.__anext__()
        except StopAsyncIteration:
            heapq.heappop(self._heap)
            return value

        heapq.heapreplace(self._heap, self._create_heap_item(new_value, iterator=it, order=order))

        return value

    async def flatten(self, *, lazy: bool = False) -> typing.Sequence[T]:
        """Flatten the paginator."""
        if self.limit is not None and lazy:
            return [item async for item in self]

        coros = (flatten(i) for i in self.iterators)
        lists: typing.Sequence[typing.Sequence[T]] = await asyncio.gather(*coros)  # pyright: ignore

        return list(heapq.merge(*lists, key=self._key))[: self.limit]  # pyright: ignore
