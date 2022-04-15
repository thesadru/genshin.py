"""Utilities for concurrency optimizations."""
import asyncio
import functools
import typing

__all__ = ["prevent_concurrency"]

CallableT = typing.TypeVar("CallableT", bound=typing.Callable[..., typing.Awaitable[typing.Any]])


def prevent_concurrency(func: CallableT) -> CallableT:
    """Prevent function from running concurrently.

    This should be done exclusively for functions that cache their result.
    """
    lock = asyncio.Lock()

    @functools.wraps(func)
    async def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        async with lock:
            return await func(*args, **kwargs)

    return typing.cast("CallableT", inner)
