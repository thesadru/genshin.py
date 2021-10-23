"""Utilities for iterators"""
import asyncio
import heapq
from typing import *

T = TypeVar("T")

__all__ = ["aenumerate", "aislice", "azip", "amerge"]


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


async def azip(*iterables: AsyncIterable[T]) -> AsyncIterator[Tuple[T, ...]]:
    iterators = [i.__aiter__() for i in iterables]
    while True:
        coros = (i.__anext__() for i in iterators)
        try:
            x = await asyncio.gather(*coros)
        except StopAsyncIteration:
            break
        yield tuple(x)


async def _try_gather_first(iterators: Iterable[AsyncIterator[T]]) -> List[T]:
    """Gather all the first values of iterators at once"""
    coros = (it.__anext__() for it in iterators)
    gathered = await asyncio.gather(*coros, return_exceptions=True)
    values = []
    for x in gathered:
        if isinstance(x, BaseException):
            if not isinstance(x, StopAsyncIteration):
                raise x
        else:
            values.append(x)
    return values


async def amerge(
    iterables: Iterable[AsyncIterable[T]], key: Callable[[T], Any] = None
) -> AsyncIterator[T]:
    """Async version of heapq.merge"""
    key = key or (lambda x: x)

    iterators = [i.__aiter__() for i in iterables]
    values = await _try_gather_first(iterators)

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
