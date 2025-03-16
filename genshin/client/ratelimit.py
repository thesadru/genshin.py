"""Ratelimit handlers."""

import logging
import typing

import aiohttp
from tenacity import before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from genshin import errors

LOGGER_ = logging.getLogger(__name__)
CallableT = typing.TypeVar("CallableT", bound=typing.Callable[..., typing.Awaitable[typing.Any]])


def handle_ratelimits(
    tries: int = 5,
    exception: type[errors.GenshinException] = errors.VisitsTooFrequently,
    delay: float = 0.5,
) -> typing.Callable[[CallableT], CallableT]:
    """Handle ratelimits for requests."""
    return retry(
        stop=stop_after_attempt(tries),
        wait=wait_random_exponential(multiplier=delay, min=delay),
        retry=retry_if_exception_type(exception),
        reraise=True,  # Raise the final exception after retries are exhausted
        before_sleep=before_sleep_log(LOGGER_, logging.DEBUG),
    )


def handle_request_timeouts(
    tries: int = 5,
    delay: float = 0.3,
) -> typing.Callable[[CallableT], CallableT]:
    """Handle timeout errors for requests."""
    try:
        from aiohttp_socks import ProxyError
    except ImportError:
        return retry(
            stop=stop_after_attempt(tries),
            wait=wait_random_exponential(multiplier=delay, min=delay),
            retry=retry_if_exception_type((TimeoutError, aiohttp.ClientError)),
            reraise=True,
            before_sleep=before_sleep_log(LOGGER_, logging.DEBUG),
        )
    else:
        return retry(
            stop=stop_after_attempt(tries),
            wait=wait_random_exponential(multiplier=delay, min=delay),
            retry=retry_if_exception_type((TimeoutError, aiohttp.ClientError, ProxyError)),
            reraise=True,
            before_sleep=before_sleep_log(LOGGER_, logging.DEBUG),
        )
