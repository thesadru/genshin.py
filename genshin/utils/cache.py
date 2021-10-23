"""Caching utilities"""
from __future__ import annotations

from functools import update_wrapper
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

if TYPE_CHECKING:
    from genshin.client import GenshinClient

CallableT = TypeVar("CallableT", bound=Callable[..., Awaitable[Any]])

__all__ = ["permanent_cache"]


def permanent_cache(key_func: Callable[..., Any]) -> Callable[[CallableT], CallableT]:
    """Like lru_cache except permanent and using a key"""

    def wrapper(func):
        async def inner(self: GenshinClient, *args: Any, **kwargs: Any):
            key = key_func(self, *args, **kwargs)

            if key in self._permanent_cache:
                return self._permanent_cache[key]

            x = await func(self, *args, **kwargs)
            self._permanent_cache[key] = x
            return x

        return update_wrapper(inner, func)

    return wrapper
