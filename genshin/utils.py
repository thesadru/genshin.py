import asyncio
import hashlib
import heapq
import inspect
import random
import string
import time
from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import update_wrapper
from typing import *

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    P = ParamSpec("P")
else:
    P = TypeVar("P")

T = TypeVar("T")

__all__ = [
    "generate_ds_token",
    "recognize_server",
    "get_short_lang_code",
    "get_browser_cookies",
    "permanent_cache",
    "amerge",
]


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
    return lang if "zh" in lang else lang.split("-")[0]


def get_browser_cookies(browser: str = None) -> Dict[str, str]:
    """Gets cookies from your browser for later storing.

    If a specific browser is set, gets data from that browser only.
    Avalible browsers: chrome, chromium, opera, edge, firefox
    """
    try:
        import browser_cookie3
    except ImportError as e:
        raise ImportError("Missing optional dependency browser_cookie3") from e

    load = getattr(browser_cookie3, browser.lower()) if browser else browser_cookie3.load

    allowed_cookies = {"ltuid", "ltoken", "account_id", "cookie_token"}
    return {
        c.name: c.value
        for domain in ("mihoyo", "hoyolab")
        for c in load(domain_name=domain)
        if c.name in allowed_cookies and c.value is not None
    }


def permanent_cache(*params: str) -> Callable[[T], T]:
    """Like lru_cache except permanent and only caches based on some parameters"""
    cache: Dict[Any, Any] = {}

    def wrapper(func):
        sig = inspect.signature(func)

        async def inner(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            # since the amount of arguments is constant we can just save the values
            key = tuple(v for k, v in bound.arguments.items() if k in params)

            if key in cache:
                return cache[key]
            r = await func(*args, **kwargs)
            if r is not None:
                cache[key] = r
            return r

        inner.cache = cache
        return update_wrapper(inner, func)

    return wrapper  # type: ignore


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

    heap = [
        [key(value), order, value, it.__anext__]
        for order, (it, value) in enumerate(zip(iterators, values))
    ]

    # the rest is simply heapq.merge:
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


# for the convenience of the user we hide these windows errors:
def _silence_event_loop_closed(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise

    return wrapper


_ProactorBasePipeTransport.__del__ = _silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
