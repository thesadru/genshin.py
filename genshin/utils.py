
import hashlib
import heapq
import random
import string
import time
from typing import (Any, AsyncIterable, AsyncIterator, Callable, Iterable,
                    TypeVar)

T = TypeVar("T")

def generate_ds_token(salt: str) -> str:
    """Creates a new ds token for authentication."""
    t = int(time.time())
    r = "".join(random.choices(string.ascii_letters, k=6))
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()
    return f"{t},{r},{h}"


def recognize_server(uid: int) -> str:
    """Recognizes which server a UID is from."""
    server = {
        "1": "cn_gf01",
        "5": "cn_qd01",
        "6": "os_usa",
        "7": "os_euro",
        "8": "os_asia",
        "9": "os_cht",
    }.get(str(uid)[0])

    if server:
        return server
    else:
        raise Exception(f"UID {uid} isn't associated with any server")

def get_short_lang_code(lang: str) -> str:
    """Returns an alternative short lang code"""
    return lang if 'zh' in lang else lang.split('-')[0]

async def heapq_merge(iterables: Iterable[AsyncIterable[T]], key: Callable[[T], Any] = None) -> AsyncIterator[T]:
    """Async version of heapq.merge"""
    key = key or (lambda x: x)
    heap = []

    for order, iterable in enumerate(iterables):
        it = iterable.__aiter__()
        try:
            value = await it.__anext__()
            heap.append([key(value), order, value, it.__anext__])
        except StopAsyncIteration:
            pass
    
    heapq.heapify(heap)

    while len(heap) > 1:
        try:
            while True:
                key_value, order, value, next = s = heap[0]
                yield value
                value = await next()
                s[0] = key(value)
                s[2] = value
                heapq.heapreplace(heap, s)
        except StopAsyncIteration:
            heapq.heappop(heap)
    
    if heap:
        key_value, order, value, next = heap[0]
        yield value
        async for item in next.__self__:
            yield item
