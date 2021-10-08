"""Cache utils"""
import inspect
from functools import update_wrapper
from typing import Any, Awaitable, Callable, Dict, TypeVar

CallableT = TypeVar("CallableT", bound=Callable[..., Awaitable[Any]])

__all__ = ["permanent_cache"]


def permanent_cache(*params: str) -> Callable[[CallableT], CallableT]:
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

    return wrapper
