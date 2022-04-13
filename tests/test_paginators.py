import typing

import pytest

from genshin import paginators


class CountingPaginator(paginators.Paginator[int]):
    _index = 0

    async def __anext__(self) -> int:
        if self._index >= 5:
            self._complete()

        self._index += 1
        return self._index


@pytest.fixture(name="counting_paginator")
def counting_paginator_fixture():
    return CountingPaginator()


async def test_paginator_iter(counting_paginator: paginators.Paginator[int]):
    async for value in counting_paginator:
        assert 1 <= value <= 5


async def test_paginator_flatten():
    paginator = CountingPaginator()
    assert await paginator.flatten() == [1, 2, 3, 4, 5]

    paginator = CountingPaginator()
    assert await paginator == [1, 2, 3, 4, 5]


async def test_paginator_next(counting_paginator: paginators.Paginator[int]):
    assert await counting_paginator.next() == 1


async def test_paginator_next_empty():
    paginator = paginators.base.BasicPaginator(())

    with pytest.raises(StopAsyncIteration):
        await paginator.__anext__()

    with pytest.raises(LookupError):
        await paginator.next()


async def test_buffered_paginator():
    class MockBufferedPaginator(paginators.BufferedPaginator[int]):
        async def next_page(self) -> typing.Sequence[int]:
            index = self._counter - 1
            return list(range(index, index + 5))

    paginator = MockBufferedPaginator(limit=12)
    assert not paginator.exhausted

    values = await paginator.flatten()
    assert values == list(range(0, 12))

    assert paginator.exhausted


async def test_merged_paginator():
    # from heapq.merge doc
    sequences = [[1, 3, 5, 7], [0, 2, 4, 8], [5, 10, 15, 20], [], [25]]
    iterators = [paginators.base.aiterate(x) for x in sequences]

    paginator = paginators.MergedPaginator(iterators)
    assert await paginator.flatten() == [0, 1, 2, 3, 4, 5, 5, 7, 8, 10, 15, 20, 25]


async def test_merged_paginator_with_key():
    # from heapq.merge doc
    sequences = [["dog", "horse"], [], ["cat", "fish", "kangaroo"], ["rhinoceros"]]
    iterators = [paginators.base.aiterate(x) for x in sequences]

    paginator = paginators.MergedPaginator(iterators, key=len, limit=5)
    assert await paginator.flatten(lazy=True) == ["dog", "cat", "fish", "horse", "kangaroo"]
