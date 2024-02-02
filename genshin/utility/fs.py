"""File system related utilities."""

import functools
import pathlib
import tempfile
import typing

__all__ = ["get_browser_cookies"]

DOMAINS: typing.Final[typing.Sequence[str]] = ("mihoyo", "hoyolab", "hoyoverse")
ALLOWED_COOKIES: typing.Final[typing.Sequence[str]] = (
    "ltuid",
    "ltoken",
    "account_id",
    "cookie_token",
    "ltoken_v2",
    "ltmid_v2",
    "cookie_token_v2",
    "account_mid_v2",
)


def _get_browser_cookies(
    browser: typing.Optional[str] = None,
    *,
    cookie_file: typing.Optional[str] = None,
    domains: typing.Optional[typing.Sequence[str]] = None,
) -> typing.Mapping[str, str]:
    """Get cookies using browser-cookie3 from several domains.

    Available browsers: chrome, chromium, opera, edge, firefox.
    """
    import browser_cookie3  # pyright: ignore

    if browser is None:
        if cookie_file is not None:
            raise TypeError("Cannot use a cookie_file without a specified browser.")

        loader = browser_cookie3.load  # pyright: ignore

    else:
        if browser not in ("chrome", "chromium", "opera", "brave", "edge", "firefox"):
            raise ValueError(f"Unsupported browser: {browser}")

        loader = getattr(browser_cookie3, browser)  # pyright: ignore
        loader = functools.partial(loader, cookie_file=cookie_file)

    loader = typing.cast("typing.Callable[..., typing.Any]", loader)

    domains = domains or [""]
    return {cookie.name: str(cookie.value) for domain in domains for cookie in loader(domain_name=domain)}


def get_browser_cookies(
    browser: typing.Optional[str] = None,
    *,
    cookie_file: typing.Optional[str] = None,
    domains: typing.Sequence[str] = DOMAINS,
    allowed_cookies: typing.Sequence[str] = ALLOWED_COOKIES,
) -> typing.Mapping[str, str]:
    """Get hoyolab authentication cookies from your browser for later storing.

    Available browsers: chrome, chromium, opera, edge, firefox.
    """
    cookies = _get_browser_cookies(browser, cookie_file=cookie_file, domains=domains)
    return {name: value for name, value in cookies.items() if name in allowed_cookies}


def get_tempdir() -> pathlib.Path:
    """Get the temporary directory to be used by genshin.py."""
    tempdir = pathlib.Path(tempfile.gettempdir())
    directory = tempdir / "genshinpy"
    directory.mkdir(exist_ok=True, parents=True)

    return directory


if __name__ == "__main__":
    print(get_browser_cookies("chrome"))  # noqa
