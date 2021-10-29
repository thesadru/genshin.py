"""Caching utilities"""
import json
import os
from functools import update_wrapper
from typing import Any, Callable, Coroutine, Tuple, TypeVar

from .misc import get_tempdir

CallableT = TypeVar("CallableT", bound=Callable[..., Coroutine[Any, Any, Any]])

__all__ = ["perm_cache"]


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
