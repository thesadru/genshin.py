"""Ratelimit handlers."""

import asyncio
import functools
import typing

from genshin import errors

CallableT = typing.TypeVar("CallableT", bound=typing.Callable[..., typing.Awaitable[typing.Any]])


def handle_ratelimits(
    tries: int = 5,
    exception: type[errors.GenshinException] = errors.VisitsTooFrequently,
    delay: float = 0.3,
    backoff_factor: float = 2.0,
) -> typing.Callable[[CallableT], CallableT]:
    """Handle ratelimits for requests."""

    def wrapper(func: typing.Callable[..., typing.Awaitable[typing.Any]]) -> typing.Any:
        @functools.wraps(func)
        async def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            current_delay = delay
            for attempt in range(tries):
                try:
                    x = await func(*args, **kwargs)
                except exception:
                    if attempt < tries - 1:  # No need to sleep on last attempt
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        raise exception({}, f"Got ratelimited {tries} times in a row")
                else:
                    return x

        return inner

    return wrapper
