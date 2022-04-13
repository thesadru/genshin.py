"""File system related utilities."""
import functools
import os
import pathlib
import tempfile
import typing

__all__ = ["get_browser_cookies"]

DOMAINS: typing.Final[typing.Sequence[str]] = ("mihoyo", "hoyolab", "hoyoverse")
ALLOWED_COOKIES: typing.Final[typing.Sequence[str]] = ("ltuid", "ltoken", "account_id", "cookie_token")


def _fix_windows_chrome_temp() -> None:
    # temporary non-invasive fix for chrome
    # https://github.com/borisbabic/browser_cookie3/issues/106#issuecomment-1000200958
    try:
        local_appdata = pathlib.Path(os.environ["LOCALAPPDATA"])
        chrome_dir = local_appdata / "Google/Chrome/User Data/Default"

        os.link(chrome_dir / "Network/Cookies", chrome_dir / "Cookies")

    except (OSError, KeyError):
        pass


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

    _fix_windows_chrome_temp()

    loader: typing.Callable[..., typing.Any]

    if browser is None:
        if cookie_file is not None:
            raise TypeError("Cannot use a cookie_file without a specified browser.")

        loader = browser_cookie3.load  # pyright: ignore

    else:
        if browser not in ("chrome", "chromium", "opera", "brave", "edge", "firefox"):
            raise ValueError(f"Unsupported browser: {browser}")

        loader = getattr(browser_cookie3, browser)  # pyright: ignore
        loader = functools.partial(loader, cookie_file=cookie_file)

    domains = domains or [""]
    return {cookie.name: cookie.value for domain in domains for cookie in loader(domain_name=domain)}


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


def get_tempdir() -> str:
    """Get the temporary directory to be used by genshin.py."""
    directory = os.path.join(tempfile.gettempdir(), "genshin.py")
    os.makedirs(directory, exist_ok=True)
    return directory


if __name__ == "__main__":
    print(get_browser_cookies("chrome"))  # noqa
