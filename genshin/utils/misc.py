"""Miscalenious utilities"""
import hashlib
import random
import string
import time
from asyncio.proactor_events import _ProactorBasePipeTransport
from typing import Dict

__all__ = [
    "generate_ds_token",
    "recognize_server",
    "get_short_lang_code",
    "get_browser_cookies",
]


def generate_ds_token(salt: str) -> str:
    """Creates a new ds token for authentication."""
    t = int(time.time())
    r = "".join(random.choices(string.ascii_letters, k=6))
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()
    return f"{t},{r},{h}"


def recognize_server(uid: int) -> str:
    """Recognizes which server a UID is from."""
    server = {
        "1": "cn_gf01",
        "5": "cn_qd01",
        "6": "os_usa",
        "7": "os_euro",
        "8": "os_asia",
        "9": "os_cht",
    }.get(str(uid)[0])

    if server:
        return server
    else:
        raise ValueError(f"UID {uid} isn't associated with any server")


def get_short_lang_code(lang: str) -> str:
    """Returns an alternative short lang code"""
    return lang if "zh" in lang else lang.split("-")[0]


def get_browser_cookies(browser: str = None) -> Dict[str, str]:
    """Gets cookies from your browser for later storing.

    If a specific browser is set, gets data from that browser only.
    Avalible browsers: chrome, chromium, opera, edge, firefox
    """
    import browser_cookie3

    load = getattr(browser_cookie3, browser.lower()) if browser else browser_cookie3.load

    allowed_cookies = {"ltuid", "ltoken", "account_id", "cookie_token"}
    return {
        c.name: c.value
        for domain in ("mihoyo", "hoyolab")
        for c in load(domain_name=domain)
        if c.name in allowed_cookies and c.value is not None
    }


# for the convenience of the user we hide these windows errors:
def _silence_event_loop_closed(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise

    return wrapper


_ProactorBasePipeTransport.__del__ = _silence_event_loop_closed(_ProactorBasePipeTransport.__del__)  # type: ignore
