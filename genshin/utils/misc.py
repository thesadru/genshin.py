"""Miscalenious utilities"""
import asyncio
import functools
import os
import tempfile
from asyncio.proactor_events import _ProactorBasePipeTransport
from typing import Any, Callable, Coroutine, Dict, Type, TypeVar

from .. import errors

CallableT = TypeVar("CallableT", bound=Callable[..., Coroutine[Any, Any, Any]])

__all__ = ["get_browser_cookies", "get_tempdir", "handle_ratelimits"]


def get_browser_cookies(browser: str = None) -> Dict[str, str]:
    """Gets cookies from your browser for later storing.

    Avalible browsers: chrome, chromium, opera, edge, firefox

    :param browser: The browser to extract the cookies from
    :returns: The extracted cookies
    """
    if browser and browser not in ("chrome", "chromium", "opera", "edge", "firefox"):
        raise ValueError(f"Unsupported browser: {browser}")

    import browser_cookie3

    load = getattr(browser_cookie3, browser.lower()) if browser else browser_cookie3.load

    allowed_cookies = {"ltuid", "ltoken", "account_id", "cookie_token"}
    return {
        c.name: c.value
        for domain in ("mihoyo", "hoyolab")
        for c in load(domain_name=domain)
        if c.name in allowed_cookies and c.value is not None
    }


def get_tempdir():
    """Gets the temporary directory to be used by genshin.py"""
    directory = os.path.join(tempfile.gettempdir(), "genshin.py")
    os.makedirs(directory, exist_ok=True)
    return directory


def handle_ratelimits(
    tries: int = 5,
    exception: Type[errors.GenshinException] = errors.VisitsTooFrequently,
    delay: float = 0.3,
) -> Callable[[CallableT], CallableT]:
    """Handles ratelimits for requests"""
    # TODO: Support exponential backoff

    def wrapper(func) -> Any:
        async def inner(self, *args: Any, **kwargs: Any) -> Any:
            for _ in range(tries):
                try:
                    x = await func(self, *args, **kwargs)
                except exception:
                    await asyncio.sleep(delay)
                else:
                    return x
            else:
                raise exception({}, f"Got ratelimited {tries} times in a row")

        return functools.update_wrapper(inner, func)

    return wrapper


# for the convenience of the user we hide these windows errors:
def _silence_event_loop_closed(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise

    return wrapper


_ProactorBasePipeTransport.__del__ = _silence_event_loop_closed(_ProactorBasePipeTransport.__del__)  # type: ignore # noqa
