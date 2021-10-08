"""Utilities for iterators"""
import asyncio
import heapq
from typing import *

T = TypeVar("T")

__all__ = ["amerge", "aenumerate", "aislice"]


async def aenumerate(iterable: AsyncIterable[T], start: int = 0) -> AsyncIterator[Tuple[int, T]]:
    i = start
    async for x in iterable:
        yield i, x
        i += 1


async def aislice(iterable: AsyncIterable[T], stop: int = None) -> AsyncIterator[T]:
    """Slices an async iterable"""
    async for i, x in aenumerate(iterable, start=1):
        yield x

        if stop and i >= stop:
            return


async def _try_gather(coros: Iterable[Awaitable[T]]) -> List[T]:
    _failed = object()

    async def maybe(coro) -> Any:
        try:
            return await coro
        except:
            return _failed

    values = await asyncio.gather(*(maybe(coro) for coro in coros))
    return [x for x in values if x is not _failed]


async def amerge(
    iterables: Iterable[AsyncIterable[T]], key: Callable[[T], Any] = None
) -> AsyncIterator[T]:
    """Async version of heapq.merge"""
    key = key or (lambda x: x)

    # for optimization we get all the first values at once
    iterators = [i.__aiter__() for i in iterables]
    values = await _try_gather(it.__anext__() for it in iterators)

    heap: List[List[Any]] = [
        [key(value), order, value, it.__anext__]
        for order, (it, value) in enumerate(zip(iterators, values))
    ]

    # the rest is simply heapq.merge:
    heapq.heapify(heap)

    while len(heap) > 1:
        try:
            while True:
                _, _, value, anext = s = heap[0]
                yield value
                value = await anext()
                s[0] = key(value)
                s[2] = value
                heapq.heapreplace(heap, s)
        except StopAsyncIteration:
            heapq.heappop(heap)

    if heap:
        _, _, value, anext = heap[0]
        yield value
        async for item in anext.__self__:
            yield item
