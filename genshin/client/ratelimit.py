"""Ratelimit handlers."""

import asyncio
import functools
import typing

from genshin import errors

CallableT = typing.TypeVar("CallableT", bound=typing.Callable[..., typing.Awaitable[typing.Any]])


def handle_ratelimits(
    tries: int = 5,
    exception: typing.Type[errors.GenshinException] = errors.VisitsTooFrequently,
    delay: float = 0.3,
) -> typing.Callable[[CallableT], CallableT]:
    """Handle ratelimits for requests."""
    # TODO: Support exponential backoff

    def wrapper(func: typing.Callable[..., typing.Awaitable[typing.Any]]) -> typing.Any:
        @functools.wraps(func)
        async def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            for _ in range(tries):
                try:
                    x = await func(*args, **kwargs)
                except exception:
                    await asyncio.sleep(delay)
                else:
                    return x
            else:
                raise exception({}, f"Got ratelimited {tries} times in a row")

        return inner

    return wrapper
