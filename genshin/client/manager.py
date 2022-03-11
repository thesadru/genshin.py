"""Cookie managers for making authenticated requests."""
from __future__ import annotations

import abc
import http.cookies
import logging
import typing

import aiohttp
import aiohttp.typedefs

from genshin import errors, types
from genshin.utility import fs as fs_utility

from . import ratelimit

_LOGGER = logging.getLogger(__name__)

__all__ = ["AbstractCookieManager", "CookieManager", "RotatingCookieManager"]

CookieOrHeader = typing.Union["http.cookies.BaseCookie[typing.Any]", typing.Mapping[typing.Any, typing.Any], str]
AnyCookieOrHeader = typing.Union[CookieOrHeader, typing.Sequence[CookieOrHeader]]


def parse_cookie(cookie: typing.Optional[CookieOrHeader]) -> typing.Dict[str, str]:
    """Parse a cookie or header into a cookie mapping."""
    if cookie is None:
        return {}

    if isinstance(cookie, str):
        cookie = http.cookies.SimpleCookie(cookie)

    return {str(k): v.value if isinstance(v, http.cookies.Morsel) else str(v) for k, v in cookie.items()}


class AbstractCookieManager(abc.ABC):
    """A cookie manager for making requests."""

    region: types.Region = types.Region.OVERSEAS

    @classmethod
    def from_cookies(
        cls,
        cookies: typing.Optional[AnyCookieOrHeader] = None,
        region: types.Region = types.Region.OVERSEAS,
    ) -> AbstractCookieManager:
        """Create an arbitrary cookie manager implementation instance."""
        if isinstance(cookies, typing.Sequence):
            return RotatingCookieManager(cookies, region=region)

        return CookieManager(cookies, region)

    @classmethod
    def from_browser_cookies(
        cls,
        browser: typing.Optional[str] = None,
        region: types.Region = types.Region.OVERSEAS,
    ) -> CookieManager:
        """Create a cookie manager with browser cookies."""
        manager = CookieManager(region=region)
        manager.set_browser_cookies(browser)

        return manager

    @property
    @abc.abstractmethod
    def available(self) -> bool:
        """Whether the authentication cookies are available."""

    @property
    def user_id(self) -> typing.Optional[int]:
        """The id of the user that owns cookies.

        Returns None if not found or not applicable.
        """
        return None

    def get_user_id(self, fallback: typing.Optional[int]) -> int:
        """Get the id of the user that owns cookies.

        Raises an error if not found and fallback is not provided.
        """
        if fallback:
            return fallback

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
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Make a request towards any json resource."""
        async with self.create_session() as session:
            async with session.request(method, str_or_url, **kwargs) as response:
                data = await response.json()

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


class CookieManager(AbstractCookieManager):
    """Standard implementation of the cookie manager."""

    _cookies: typing.Dict[str, str]

    def __init__(
        self,
        cookies: typing.Optional[CookieOrHeader] = None,
        region: types.Region = types.Region.OVERSEAS,
    ) -> None:
        self.cookies = parse_cookie(cookies)
        self.region = region

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.cookies})"

    @property
    def cookies(self) -> typing.Mapping[str, str]:
        """Cookies used for authentication"""
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
    def jar(self) -> http.cookies.SimpleCookie[str]:
        """A client cookie jar."""
        return http.cookies.SimpleCookie(self.cookies)

    def set_cookies(
        self,
        cookies: typing.Optional[CookieOrHeader] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, str]:
        """Parse and set cookies."""
        if not bool(cookies) ^ bool(kwargs):
            raise TypeError("Cannot use both positional and keyword arguments at once")

        self.cookies = parse_cookie(cookies or kwargs)
        return self.cookies

    def set_browser_cookies(self, browser: typing.Optional[str] = None) -> typing.Mapping[str, str]:
        """Extract cookies from your browser and set them as client cookies.

        Available browsers: chrome, chromium, opera, edge, firefox.
        """
        self.cookies = fs_utility.get_browser_cookies(browser)
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
        if not self.cookies:
            raise RuntimeError("Tried to make a request before setting cookies")

        return await self._request(method, url, cookies=self.cookies, **kwargs)


class RotatingCookieManager(AbstractCookieManager):
    """Cookie Manager with rotating cookies."""

    MAX_USES: typing.ClassVar[int] = 30

    _cookies: typing.List[typing.Tuple[typing.Dict[str, str], int]]

    def __init__(
        self,
        cookies: typing.Optional[typing.Sequence[CookieOrHeader]] = None,
        region: types.Region = types.Region.OVERSEAS,
    ) -> None:
        self.cookies = [parse_cookie(cookie) for cookie in cookies or []]
        self.region = region

    @property
    def cookies(self) -> typing.Sequence[typing.Mapping[str, str]]:
        """Cookies used for authentication"""
        self._sort_cookies()
        return [cookie for cookie, _ in self._cookies]

    @cookies.setter
    def cookies(self, cookies: typing.Optional[typing.Sequence[CookieOrHeader]]) -> None:
        if not cookies:
            self._cookies = []
            return

        self._cookies = [(parse_cookie(cookie), 0) for cookie in cookies]
        self._sort_cookies()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len={len(self._cookies)}>"

    @property
    def available(self) -> bool:
        return bool(self._cookies)

    def set_cookies(
        self,
        cookies: typing.Optional[typing.Sequence[CookieOrHeader]] = None,
    ) -> typing.Sequence[typing.Mapping[str, str]]:
        """Parse and set cookies."""
        self.cookies = [parse_cookie(cookie) for cookie in cookies or []]
        return self.cookies

    def _sort_cookies(self) -> None:
        """Sort cookies by remaining uses."""
        # TODO: different strategy
        self._cookies.sort(key=lambda x: 0 if x[1] >= self.MAX_USES else x[1], reverse=True)

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

        self._sort_cookies()

        for index, (cookie, uses) in enumerate(self._cookies.copy()):
            try:
                data = await self._request(method, url, cookies=cookie, **kwargs)
            except errors.TooManyRequests:
                _LOGGER.debug("Putting cookie %s on cooldown.", cookie.get("account_id") or cookie.get("ltuid"))
                self._cookies[index] = (cookie, self.MAX_USES)
            else:
                self._cookies[index] = (cookie, 1 if uses >= self.MAX_USES else uses + 1)
                return data

        msg = "All cookies have hit their request limit of 30 accounts per day."
        raise errors.TooManyRequests({"retcode": 10101}, msg)
