"""Base abc client."""
import base64
import json as stdjson
import logging
import os
import typing
import urllib.parse

import aiohttp.typedefs
import yarl

from genshin import constants, types
from genshin.client import manager, routes
from genshin.utility import ds
from genshin.utility import genshin as genshin_utility


class BaseClient:
    """A simple HTTP client for API endpoints."""

    WEBSTATIC_URL = "https://webstatic-sea.hoyoverse.com/"

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"  # noqa: E501

    logger: logging.Logger = logging.getLogger(__name__)

    cookie_manager: manager.BaseCookieManager
    _authkey: typing.Optional[str] = None
    _lang: str

    def __init__(
        self,
        cookies: typing.Optional[manager.AnyCookieOrHeader] = None,
        *,
        authkey: typing.Optional[str] = None,
        lang: str = "en-us",
        region: types.Region = types.Region.OVERSEAS,
        debug: bool = False,
    ) -> None:
        self.cookie_manager = manager.BaseCookieManager.from_cookies(cookies)
        self.authkey = authkey
        self.lang = lang
        self.region = region
        self.debug = debug

    def __repr__(self) -> str:
        return f"<{type(self).__name__} lang={self.lang!r} hoyolab_uid={self.hoyolab_uid} debug={self.debug}>"

    @property
    def hoyolab_uid(self) -> typing.Optional[int]:
        """The logged-in user's hoyolab uid.

        Returns None if not found or not applicable.
        """
        return self.cookie_manager.user_id

    @property
    def lang(self) -> str:
        """The default language, defaults to "en-us" """
        return self._lang

    @lang.setter
    def lang(self, lang: str) -> None:
        if lang not in constants.LANGS:
            raise ValueError(f"{lang} is not a valid language, must be one of: " + ", ".join(constants.LANGS))

        self._lang = lang

    @property
    def authkey(self) -> typing.Optional[str]:
        """The default genshin authkey used for paginators."""
        return self._authkey

    @authkey.setter
    def authkey(self, authkey: typing.Optional[str]) -> None:
        if authkey is not None:
            authkey = urllib.parse.unquote(authkey)

            try:
                base64.b64decode(authkey, validate=True)
            except Exception as e:
                raise ValueError("authkey is not a valid base64 encoded string") from e

        self._authkey = authkey

    @property
    def debug(self) -> bool:
        """Whether the debug logs are being shown in stdout"""
        return logging.getLogger("genshin").level == logging.DEBUG

    @debug.setter
    def debug(self, debug: bool) -> None:
        logging.basicConfig()
        level = logging.DEBUG if debug else logging.NOTSET
        logging.getLogger("genshin").setLevel(level)

    def set_cookies(self, cookies: typing.Optional[manager.AnyCookieOrHeader] = None, **kwargs: typing.Any) -> None:
        """Parse and set cookies."""
        if not bool(cookies) ^ bool(kwargs):
            raise TypeError("Cannot use both positional and keyword arguments at once")

        self.cookie_manager = manager.BaseCookieManager.from_cookies(cookies or kwargs, region=self.region)

    def set_browser_cookies(self, browser: typing.Optional[str] = None) -> None:
        """Extract cookies from your browser and set them as client cookies.

        Available browsers: chrome, chromium, opera, edge, firefox.
        """
        self.cookie_manager = manager.BaseCookieManager.from_browser_cookies(browser, region=self.region)

    def set_authkey(self, authkey: typing.Optional[str] = None) -> None:
        """Set an authkey for wish & transaction logs.

        Accepts an authkey, a url containing an authkey or a path towards a logfile.
        """
        if authkey is None or os.path.isfile(authkey):
            authkey = genshin_utility.get_authkey(authkey)
        else:
            authkey = genshin_utility.extract_authkey(authkey) or authkey

        self.authkey = authkey

    async def _request_hook(
        self,
        method: str,
        url: aiohttp.typedefs.StrOrURL,
        *,
        params: typing.Optional[typing.Mapping[str, str]] = None,
        data: typing.Any = None,
        **kwargs: typing.Any,
    ) -> None:
        """Perform an action before a request.

        Debug logging by default.
        """
        url = yarl.URL(url)
        if params:
            params = {k: v for k, v in params.items() if k != "authkey"}
            url = url.with_query(params)

        string = f"{method} {url}"
        if data:
            string += "\n" + stdjson.dumps(data, separators=(",", ":"))

        self.logger.debug(string)

    async def request(
        self,
        url: aiohttp.typedefs.StrOrURL,
        *,
        method: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, str]] = None,
        data: typing.Any = None,
        headers: typing.Optional[aiohttp.typedefs.LooseHeaders] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request and return a parsed json response."""
        headers = dict(headers or {})
        headers["User-Agent"] = self.USER_AGENT

        if method is None:
            method = "POST" if data else "GET"

        await self._request_hook(method, url, params=params, data=data, headers=headers, **kwargs)

        return await self.cookie_manager.request(
            url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            **kwargs,
        )

    async def request_webstatic(
        self,
        url: aiohttp.typedefs.StrOrURL,
        *,
        headers: typing.Optional[aiohttp.typedefs.LooseHeaders] = None,
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Request a static json file."""
        url = yarl.URL(self.WEBSTATIC_URL).join(yarl.URL(url))

        headers = dict(headers or {})
        headers["user-agent"] = self.USER_AGENT

        async with self.cookie_manager.create_session() as session:
            async with session.get(url, headers=headers, **kwargs) as r:
                r.raise_for_status()
                data = await r.json()

        return data

    async def request_hoyolab(
        self,
        url: aiohttp.typedefs.StrOrURL,
        *,
        lang: typing.Optional[str] = None,
        method: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, str]] = None,
        data: typing.Any = None,
        headers: typing.Optional[aiohttp.typedefs.LooseHeaders] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request any hoyolab endpoint."""
        if lang not in constants.LANGS and lang is not None:
            raise ValueError(f"{lang} is not a valid language, must be one of: " + ", ".join(constants.LANGS))

        url = routes.TAKUMI_URL.get_url().join(yarl.URL(url))

        headers = {
            "x-rpc-app_version": "1.5.0",
            "x-rpc-client_type": "4",
            "x-rpc-language": lang or self.lang,
            "ds": ds.generate_dynamic_secret(constants.DS_SALT[self.region]),
        }

        data = await self.request(url, method=method, params=params, headers=headers, **kwargs)

        return data
