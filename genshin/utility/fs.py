"""File system related utilities."""
import http.cookiejar
import os
import tempfile
import typing

DOMAINS = ("mihoyo", "hoyolab", "hoyoverse")


def get_browser_cookies(
    browser: typing.Optional[str] = None,
    domains: typing.Sequence[str] = DOMAINS,
) -> typing.Dict[str, str]:
    """Get cookies from your browser for later storing.

    Available browsers: chrome, chromium, opera, edge, firefox.
    """
    if browser and browser not in ("chrome", "chromium", "opera", "edge", "firefox"):
        raise ValueError(f"Unsupported browser: {browser}")

    import browser_cookie3

    load: typing.Callable[..., http.cookiejar.CookieJar] = getattr(browser_cookie3, browser or "load")  # type: ignore

    allowed_cookies = {"ltuid", "ltoken", "account_id", "cookie_token"}
    return {
        c.name: c.value
        for domain in domains
        for c in load(domain_name=domain)
        if c.name in allowed_cookies and c.value is not None
    }


def get_tempdir() -> str:
    """Get the temporary directory to be used by genshin.py."""
    directory = os.path.join(tempfile.gettempdir(), "genshin.py")
    os.makedirs(directory, exist_ok=True)
    return directory
