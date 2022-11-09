"""Cookie managers for making authenticated requests."""
from __future__ import annotations

import abc
import functools
import http.cookies
import logging
import typing
import warnings

import aiohttp
import aiohttp.typedefs
import yarl

from genshin import errors, types
from genshin.client import routes
from genshin.utility import fs as fs_utility

from . import ratelimit

_LOGGER = logging.getLogger(__name__)

__all__ = [
    "BaseCookieManager",
    "CookieManager",
    "InternationalCookieManager",
    "RotatingCookieManager",
    "complete_cookies",
]

CookieOrHeader = typing.Union["http.cookies.BaseCookie[typing.Any]", typing.Mapping[typing.Any, typing.Any], str]
AnyCookieOrHeader = typing.Union[CookieOrHeader, typing.Sequence[CookieOrHeader]]

T = typing.TypeVar("T")
CallableT = typing.TypeVar("CallableT", bound="typing.Callable[..., object]")
AsyncCallableT = typing.TypeVar("AsyncCallableT", bound="typing.Callable[..., typing.Awaitable[object]]")
MaybeSequence = typing.Union[T, typing.Sequence[T]]


def parse_cookie(cookie: typing.Optional[CookieOrHeader]) -> typing.Dict[str, str]:
    """Parse a cookie or header into a cookie mapping."""
    if cookie is None:
        return {}

    if isinstance(cookie, str):
        cookie = http.cookies.SimpleCookie(cookie)

    return {str(k): v.value if isinstance(v, http.cookies.Morsel) else str(v) for k, v in cookie.items()}


class BaseCookieManager(abc.ABC):
    """A cookie manager for making requests."""

    _proxy: typing.Optional[yarl.URL] = None

    @classmethod
    def from_cookies(cls, cookies: typing.Optional[AnyCookieOrHeader] = None) -> BaseCookieManager:
        """Create an arbitrary cookie manager implementation instance."""
        if isinstance(cookies, typing.Sequence) and not isinstance(cookies, str):
            return RotatingCookieManager(cookies)

        return CookieManager(cookies)

    @classmethod
    def from_browser_cookies(cls, browser: typing.Optional[str] = None) -> CookieManager:
        """Create a cookie manager with browser cookies."""
        manager = CookieManager()
        manager.set_browser_cookies(browser)

        return manager

    @property
    def available(self) -> bool:
        """Whether the authentication cookies are available."""
        return True

    @property
    def multi(self) -> bool:
        """Whether the cookie manager contains multiple cookies and therefore should not cache private data."""
        return False

    @property
    def user_id(self) -> typing.Optional[int]:
        """The id of the user that owns cookies.

        Returns None if not found or not applicable.
        """
        return None

    @property
    def proxy(self) -> typing.Optional[yarl.URL]:
        """Proxy for http(s) requests."""
        return self._proxy

    @proxy.setter
    def proxy(self, proxy: typing.Optional[aiohttp.typedefs.StrOrURL]) -> None:
        if proxy is None:
            self._proxy = None
            return

        proxy = yarl.URL(proxy)
        if str(proxy.scheme) not in ("https", "http", "ws", "wss"):
            raise ValueError("Proxy URL must have a valid scheme.")

        self._proxy = proxy

    def get_user_id(self) -> int:
        """Get the id of the user that owns cookies.

        Raises an error if not found and fallback is not provided.
        """
        if self.user_id:
            return self.user_id

        if self.available:
            raise ValueError(f"Hoyolab ID must be provided when using {self.__class__}")

        raise ValueError("No cookies have been provided.")

    def create_session(self, **kwargs: typing.Any) -> aiohttp.ClientSession:
        """Create a client session."""
        return aiohttp.ClientSession(
            cookie_jar=aiohttp.DummyCookieJar(),
            **kwargs,
        )

    @ratelimit.handle_ratelimits()
    async def _request(
        self,
        method: str,
        str_or_url: aiohttp.typedefs.StrOrURL,
        cookies: typing.MutableMapping[str, str],
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Make a request towards any json resource."""
        async with self.create_session() as session:
            async with session.request(method, str_or_url, proxy=self.proxy, cookies=cookies, **kwargs) as response:
                if response.content_type != "application/json":
                    content = await response.text()
                    raise errors.GenshinException(msg="Recieved a response with an invalid content type:\n" + content)

                data = await response.json()

                if not self.multi:
                    new_cookies = parse_cookie(response.cookies)
                    new_keys = new_cookies.keys() - cookies.keys()
                    if new_keys:
                        cookies.update(new_cookies)
                        _LOGGER.debug("Updating cookies for %s: %s", self.user_id, new_keys)

        if "retcode" not in data:  # special request
            return data.get("data", data)

        if data["retcode"] == 0:
            return data["data"]

        errors.raise_for_retcode(data)

    @abc.abstractmethod
    async def request(
        self,
        url: aiohttp.typedefs.StrOrURL,
        *,
        method: str = "GET",
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        data: typing.Any = None,
        json: typing.Any = None,
        cookies: typing.Optional[aiohttp.typedefs.LooseCookies] = None,
        headers: typing.Optional[aiohttp.typedefs.LooseHeaders] = None,
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Make an authenticated request."""


class CookieManager(BaseCookieManager):
    """Standard implementation of the cookie manager."""

    _cookies: typing.Dict[str, str]

    def __init__(
        self,
        cookies: typing.Optional[CookieOrHeader] = None,
    ) -> None:
        self.cookies = parse_cookie(cookies)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.cookies})"

    @property
    def cookies(self) -> typing.MutableMapping[str, str]:
        """Cookies used for authentication."""
        return self._cookies

    @cookies.setter
    def cookies(self, cookies: typing.Optional[CookieOrHeader]) -> None:
        if not cookies:
            self._cookies = {}
            return

        self._cookies = parse_cookie(cookies)

    @property
    def available(self) -> bool:
        return bool(self._cookies)

    @property
    def multi(self) -> bool:
        return False

    @property
    def jar(self) -> http.cookies.SimpleCookie[str]:
        """SimpleCookie containing the cookies."""
        return http.cookies.SimpleCookie(self.cookies)

    @property
    def header(self) -> str:
        """Header representation of cookies.

        This representation is reparsable by the manager.
        """
        return self.jar.output(header="", sep=";").strip()

    def set_cookies(
        self,
        cookies: typing.Optional[CookieOrHeader] = None,
        **kwargs: typing.Any,
    ) -> typing.MutableMapping[str, str]:
        """Parse and set cookies."""
        if not bool(cookies) ^ bool(kwargs):
            raise TypeError("Cannot use both positional and keyword arguments at once")

        self.cookies = parse_cookie(cookies or kwargs)
        return self.cookies

    def set_browser_cookies(self, browser: typing.Optional[str] = None) -> typing.Mapping[str, str]:
        """Extract cookies from your browser and set them as client cookies.

        Available browsers: chrome, chromium, opera, edge, firefox.
        """
        self.cookies = parse_cookie(fs_utility.get_browser_cookies(browser))
        return self.cookies

    @property
    def user_id(self) -> typing.Optional[int]:
        """The id of the user that owns cookies.

        Returns None if cookies are not set.
        """
        for name, value in self.cookies.items():
            if name in ("ltuid", "account_id"):
                return int(value)

        return None

    async def request(
        self,
        url: aiohttp.typedefs.StrOrURL,
        *,
        method: str = "GET",
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Make an authenticated request."""
        return await self._request(method, url, cookies=self.cookies, **kwargs)


class CookieSequence(typing.Sequence[typing.Mapping[str, str]]):
    MAX_USES: int = 30

    # {id: ({cookie}, uses), ...}
    _cookies: typing.Dict[int, typing.Tuple[typing.Dict[str, str], int]]

    def __init__(self, cookies: typing.Optional[typing.Sequence[CookieOrHeader]] = None) -> None:
        self.cookies = [parse_cookie(cookie) for cookie in cookies or []]

    @property
    def cookies(self) -> typing.Sequence[typing.Mapping[str, str]]:
        """Cookies used for authentication"""
        cookies = sorted(self._cookies.values(), key=lambda x: 0 if x[1] >= self.MAX_USES else x[1], reverse=True)
        return [cookies for cookies, _ in cookies]

    @cookies.setter
    def cookies(self, cookies: typing.Optional[typing.Sequence[CookieOrHeader]]) -> None:
        if not cookies:
            self._cookies = {}
            return

        self._cookies = {}
        for cookie in cookies:
            cookie = parse_cookie(cookie)

            account_id = cookie.get("account_id") or cookie.get("ltuid")
            if not account_id or not account_id.isdigit():
                raise ValueError(f"Cookies must contain a valid account_id or ltuid: {cookie}")

            account_id = int(account_id)

            if account_id in self._cookies:
                raise ValueError(f"Cannot use the same account_id or ltuid for multiple cookies: {account_id}.")

            self._cookies[account_id] = (cookie, 0)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len={len(self._cookies)}>"

    def __getitem__(self, index: int) -> typing.Mapping[str, str]:  # type: ignore # I can't be fucked with slices
        return self.cookies[index]

    def __len__(self) -> int:
        return len(self.cookies)

    def __iter__(self) -> typing.Iterator[typing.Mapping[str, str]]:
        return iter(self.cookies)


class RotatingCookieManager(BaseCookieManager):
    """Cookie Manager with rotating cookies."""

    _cookies: CookieSequence

    def __init__(self, cookies: typing.Optional[typing.Sequence[CookieOrHeader]] = None) -> None:
        self.set_cookies(cookies)

    @property
    def cookies(self) -> typing.Sequence[typing.Mapping[str, str]]:
        """Cookies used for authentication"""
        return self._cookies

    @cookies.setter
    def cookies(self, cookies: typing.Optional[typing.Sequence[CookieOrHeader]]) -> None:
        self._cookies.cookies = cookies  # type: ignore # mypy does not understand property setters

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len={len(self._cookies)}>"

    @property
    def available(self) -> bool:
        return bool(self._cookies)

    @property
    def multi(self) -> bool:
        return True

    def set_cookies(
        self,
        cookies: typing.Optional[typing.Sequence[CookieOrHeader]] = None,
    ) -> typing.Sequence[typing.Mapping[str, str]]:
        """Parse and set cookies."""
        self._cookies = CookieSequence(cookies)
        return self.cookies

    async def request(
        self,
        url: aiohttp.typedefs.StrOrURL,
        *,
        method: str = "GET",
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Make an authenticated request."""
        if not self.cookies:
            raise RuntimeError("Tried to make a request before setting cookies")

        for account_id, (cookie, uses) in self._cookies._cookies.copy().items():
            try:
                data = await self._request(method, url, cookies=cookie, **kwargs)
            except errors.TooManyRequests:
                _LOGGER.debug("Putting cookie %s on cooldown.", account_id)
                self._cookies._cookies[account_id] = (cookie, self._cookies.MAX_USES)
            except errors.InvalidCookies:
                warnings.warn(f"Deleting invalid cookie {cookie}")
                # prevent race conditions
                if account_id in self._cookies._cookies:
                    del self._cookies._cookies[account_id]
            else:
                self._cookies._cookies[account_id] = (cookie, 1 if uses >= self._cookies.MAX_USES else uses + 1)
                return data

        msg = "All cookies have hit their request limit of 30 accounts per day."
        raise errors.TooManyRequests({"retcode": 10101}, msg)


class InternationalCookieManager(BaseCookieManager):
    """Cookie Manager with international rotating cookies."""

    _cookies: typing.Mapping[types.Region, CookieSequence]

    def __init__(self, cookies: typing.Optional[typing.Mapping[str, MaybeSequence[CookieOrHeader]]] = None) -> None:
        self.set_cookies(cookies)

    @property
    def cookies(self) -> typing.Mapping[types.Region, typing.Sequence[typing.Mapping[str, str]]]:
        """Cookies used for authentication"""
        return self._cookies

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    @property
    def available(self) -> bool:
        return bool(self._cookies)

    @property
    def multi(self) -> bool:
        return True

    def set_cookies(
        self,
        cookies: typing.Optional[typing.Mapping[str, MaybeSequence[CookieOrHeader]]] = None,
    ) -> typing.Mapping[types.Region, typing.Sequence[typing.Mapping[str, str]]]:
        """Parse and set cookies."""
        self._cookies = {}
        if not cookies:
            return {}

        for region, regional_cookies in cookies.items():
            if not isinstance(regional_cookies, typing.Sequence):
                regional_cookies = [regional_cookies]

            self._cookies[types.Region(region)] = CookieSequence(regional_cookies)

        return self.cookies

    def guess_region(self, url: yarl.URL) -> types.Region:
        """Guess the region from the URL."""
        assert url.host is not None

        if "os" in url.host or "os" in url.path:
            return types.Region.OVERSEAS

        if "takumi" in url.host:
            return types.Region.CHINESE

        if "sg" in url.host:
            return types.Region.OVERSEAS

        return types.Region.CHINESE

    async def request(
        self,
        url: aiohttp.typedefs.StrOrURL,
        *,
        method: str = "GET",
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Make an authenticated request."""
        if not self.cookies:
            raise RuntimeError("Tried to make a request before setting cookies")

        region = self.guess_region(yarl.URL(url))

        # TODO: less copy-paste
        for account_id, (cookie, uses) in self._cookies[region]._cookies.copy().items():
            try:
                data = await self._request(method, url, cookies=cookie, **kwargs)
            except errors.TooManyRequests:
                _LOGGER.debug("Putting cookie %s on cooldown.", account_id)
                self._cookies[region]._cookies[account_id] = (cookie, self._cookies[region].MAX_USES)
            except errors.InvalidCookies:
                warnings.warn(f"Deleting invalid cookie {cookie}")
                # prevent race conditions
                if account_id in self._cookies[region]._cookies:
                    del self._cookies[region]._cookies[account_id]
            else:
                self._cookies[region]._cookies[account_id] = (
                    cookie,
                    1 if uses >= self._cookies[region].MAX_USES else uses + 1,
                )
                return data

        msg = "All cookies have hit their request limit of 30 accounts per day."
        raise errors.TooManyRequests({"retcode": 10101}, msg)


async def _fetch_cookie_token_info(
    cookies: CookieOrHeader,
    *,
    region: types.Region = types.Region.OVERSEAS,
) -> typing.Mapping[str, typing.Any]:
    """Fetch cookie token info."""
    manager = CookieManager(cookies)

    base_url = routes.ACCOUNT_URL.get_url(region)
    url = base_url / "fetch_cookie_accountinfo"

    data = await manager.request(url)

    return data["cookie_info"]


async def reload_cookie_token(
    cookies: CookieOrHeader,
    *,
    region: types.Region = types.Region.OVERSEAS,
) -> typing.MutableMapping[str, str]:
    """Reload cookie token."""
    cookies = parse_cookie(cookies)

    info = await _fetch_cookie_token_info(cookies, region=region)
    cookies["account_id"] = info["account_id"]
    cookies["cookie_token"] = info["cookie_token"]

    return cookies


async def complete_cookies(
    cookies: CookieOrHeader,
    *,
    reload: bool = True,
    region: types.Region = types.Region.OVERSEAS,
) -> typing.Mapping[str, str]:
    """Add ltoken and ltuid to a cookie with only a cookie_token and an account_id."""
    manager = CookieManager(cookies)

    if reload:
        manager.cookies = await reload_cookie_token(manager.cookies)

    base_url = routes.COMMUNITY_URL.get_url(region)
    url = base_url / "misc/wapi/langs"

    await manager.request(url)

    return manager.cookies


def no_multi(func: CallableT) -> CallableT:
    """Prevent function to be ran with a multi-cookie manager."""

    @functools.wraps(func)
    def wrapper(self: typing.Any, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        if not hasattr(self, "cookie_manager"):
            raise TypeError("Cannot use @no_multi on a plain function.")
        if self.cookie_manager.multi:
            raise RuntimeError(f"Cannot use {func.__name__} with multi-cookie managers - data is private.")

        return func(self, *args, **kwargs)

    return typing.cast("CallableT", wrapper)


def requires_cookie_token(func: AsyncCallableT) -> AsyncCallableT:
    """Prevent function to be ran without a cookie_token."""

    @functools.wraps(func)
    async def wrapper(self: typing.Any, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        if not hasattr(self, "cookie_manager"):
            raise TypeError("Cannot use @requires_cookie_token on a plain function.")
        if self.cookie_manager.multi:
            raise RuntimeError(f"Cannot use {func.__name__} with multi-cookie managers - data is private.")
        if not isinstance(self.cookie_manager, CookieManager):
            raise RuntimeError(
                f"Cannot use {func.__name__} with a custom cookie manager - a consistent API is expected."
            )
        if "cookie_token" not in self.cookie_manager.cookies or "account_id" not in self.cookie_manager.cookies:
            raise ValueError("Missing cookie_token or account_id in cookies.")

        try:
            return await func(self, *args, **kwargs)
        except errors.InvalidCookies:
            _LOGGER.debug("reloading cookie_token for %s", self.cookie_manager.cookies["account_id"])
            await reload_cookie_token(self.cookie_manager.cookies)
            return await func(self, *args, **kwargs)

    return typing.cast("AsyncCallableT", wrapper)
