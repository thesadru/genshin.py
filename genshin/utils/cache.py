"""Caching utilities"""
import json
import os
from functools import update_wrapper
from typing import Any, Callable, Coroutine, Optional, Tuple, TypeVar

from .misc import get_tempdir

CallableT = TypeVar("CallableT", bound=Callable[..., Coroutine[Any, Any, Any]])

__all__ = ["perm_cache", "get_from_static_cache", "save_to_static_cache"]


def perm_cache(key_tuple: Tuple[Any, ...], func: CallableT) -> CallableT:
    """A permanent file cache for coroutines, it just kinda works

    I originally wanted to make this wrap an already called coroutine since the syntax is easier.
    However that will always raise a resource warning which kinda sucks.
    """
    key = ":".join(map(str, key_tuple))

    filename = os.path.join(get_tempdir(), "permanent_cache.json")

    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if os.path.isfile(filename):
            with open(filename) as file:
                data = json.load(file)

            if key in data:
                return data[key]

        else:
            data = {}

        r = await func(*args, **kwargs)
        data[key] = r

        with open(filename, "w") as file:
            json.dump(data, file)

        return r

    return update_wrapper(wrapper, func)  # type: ignore


def get_from_static_cache(url: str) -> Optional[Any]:
    filename = os.path.join(get_tempdir(), "static_cache.json")

    if not os.path.isfile(filename):
        return None

    with open(filename, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            with open(filename, "w") as file:
                json.dump({}, file)
            return None

    return data.get(url)


def save_to_static_cache(url: str, x: Any) -> None:
    filename = os.path.join(get_tempdir(), "static_cache.json")

    if os.path.isfile(filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            with open(filename, "w") as file:
                json.dump({}, file)
            data = {}
    else:
        data = {}

    data[url] = x

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)
