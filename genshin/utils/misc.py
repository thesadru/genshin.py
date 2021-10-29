"""Miscalenious utilities"""
import os
import tempfile
from asyncio.proactor_events import _ProactorBasePipeTransport
from typing import Dict

__all__ = ["get_browser_cookies", "get_tempdir"]


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
    directory = os.path.join(tempfile.gettempdir(), "genshin.py")
    os.makedirs(directory, exist_ok=True)
    return directory


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
