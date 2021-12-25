from __future__ import annotations

import abc
import asyncio
import base64
import json as json_
import logging
import os
from http.cookies import SimpleCookie
from typing import *
from urllib.parse import unquote

import aiohttp
from yarl import URL

from genshin import errors, utils
from genshin.constants import LANGS

from . import cache as cache_

__all__ = ["BaseAdapter", "Adapter", "MultiCookieAdapter"]


class BaseAdapter(abc.ABC):
    """An adapter for holding authentication and making low-level requests"""

    WEBSTATIC_URL = "https://webstatic-sea.mihoyo.com/"

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"  # noqa: E501

    _authkey: Optional[str] = None
    _lang: str = "en-us"

    logger: logging.Logger = logging.getLogger(__name__)
    cache: cache_.Cache

    fetched_mi18n: bool = False

    def __init__(
        self, authkey: str = None, lang: str = "en-us", debug: bool = False, cache: cache_.Cache = None
    ) -> None:
        self.authkey = authkey
        self.lang = lang
        self.debug = debug
        self.cache = cache or cache_.Cache()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} lang={self.lang!r} debug={self.debug}>"

    @property
    def debug(self) -> bool:
        """Whether the debug logs are being shown in stdout"""
        return logging.getLogger("genshin").level == logging.DEBUG

    @debug.setter
    def debug(self, debug: bool) -> None:
        logging.basicConfig()
        level = logging.DEBUG if debug else logging.NOTSET
        logging.getLogger("genshin").setLevel(level)

    @property
    def lang(self) -> str:
        """The default language, defaults to "en-us" """
        return self._lang

    @lang.setter
    def lang(self, lang: str) -> None:
        if lang not in LANGS:
            raise ValueError(f"{lang} is not a valid language, must be one of: " + ", ".join(LANGS))

        self._lang = lang

    @property
    @abc.abstractmethod
    def cookies(self) -> Any:
        """Authentication cookies"""

    @cookies.setter
    @abc.abstractmethod
    def cookies(self) -> Any:
        ...

    @property
    def authkey(self) -> Optional[str]:
        """The default authkey"""
        return self._authkey

    @authkey.setter
    def authkey(self, authkey: Optional[str]) -> None:
        if authkey is not None:
            authkey = unquote(authkey)

            try:
                base64.b64decode(authkey, validate=True)
            except Exception as e:
                raise ValueError("authkey is not a valid base64 encoded string") from e

        self._authkey = authkey

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()

    @abc.abstractmethod
    async def close(self) -> None:
        """Close all current sessions"""

    async def _request_hook(
        self,
        method: str,
        url: Union[str, URL],
        *,
        params: Dict[str, Any] = None,
        json: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> None:
        """A hook before request, by default performs a debug log"""
        url = URL(url)
        if params:
            params = {k: v for k, v in params.items() if k != "authkey"}
            url = url.with_query(params)

        string = f"{method} {url}"
        if json:
            string += "\n" + json_.dumps(json, separators=(",", ":"))

        self.logger.debug(string)

    @abc.abstractmethod
    async def request(
        self,
        url: Union[str, URL],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request and return a parsed json response"""

    @abc.abstractmethod
    async def request_webstatic(
        self,
        url: Union[str, URL],
        **kwargs: Any,
    ) -> Any:
        """Request a static json file"""


class Adapter(BaseAdapter):
    """A standard implementation of an adapter"""

    _session: Optional[aiohttp.ClientSession] = None

    def __init__(
        self,
        cookies: Mapping[str, str] = None,
        authkey: str = None,
        *,
        lang: str = "en-us",
        debug: bool = False,
        cache: cache_.Cache = None,
    ) -> None:
        super().__init__(authkey=authkey, lang=lang, debug=debug, cache=cache)

        if cookies:
            self.cookies = cookies

    @property
    def session(self) -> aiohttp.ClientSession:
        """The current client session, created when needed"""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        return self._session

    @property
    def cookies(self) -> Mapping[str, str]:
        """The cookie jar belonging to the current session"""
        return {cookie.key: cookie.value for cookie in self.session.cookie_jar}

    @cookies.setter
    def cookies(self, cookies: Mapping[str, Any]) -> None:
        cks = {str(key): value for key, value in cookies.items()}
        self.session.cookie_jar.clear()
        self.session.cookie_jar.update_cookies(cks)

    def set_cookies(self, cookies: Union[Mapping[str, Any], str] = None, **kwargs: Any) -> Mapping[str, str]:
        """Helper cookie setter that accepts cookie headers

        :returns: The new cookies
        """
        if not bool(cookies) ^ bool(kwargs):
            raise TypeError("Cannot use both positional and keyword arguments at once")

        cookies = cookies or kwargs
        cookies = {morsel.key: morsel.value for morsel in SimpleCookie(cookies).values()}
        self.cookies = cookies
        return self.cookies

    @property
    def hoyolab_uid(self) -> Optional[int]:
        """The logged-in user's hoyolab uid"""
        for cookie in self.session.cookie_jar:
            if cookie.key in ("ltuid", "account_id"):
                return int(cookie.value)

        return None

    async def close(self) -> None:
        if self._session:
            await self._session.close()

    @utils.handle_ratelimits()
    async def request(
        self,
        url: Union[str, URL],
        method: str = "GET",
        *,
        headers: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        headers = headers or {}
        headers["User-Agent"] = self.USER_AGENT

        await self._request_hook(method, url, headers=headers, **kwargs)

        async with self.session.request(method, url, headers=headers, **kwargs) as r:
            r.raise_for_status()
            data = await r.json()

        if data["retcode"] == 0:
            return data["data"]

        errors.raise_for_retcode(data)

    async def request_webstatic(
        self,
        url: Union[str, URL],
        *,
        headers: Dict[str, Any] = None,
        cache: bool = True,
        **kwargs: Any,
    ) -> Any:
        url = URL(self.WEBSTATIC_URL).join(URL(url))

        if cache and (data := self.cache.get_from_static_cache(str(url))):
            return data

        headers = headers or {}
        headers["user-agent"] = self.USER_AGENT

        async with self.session.get(url, headers=headers, **kwargs) as r:
            r.raise_for_status()
            data = await r.json()

        if cache:
            self.cache.save_to_static_cache(str(url), data)

        return data


class MultiCookieAdapter(BaseAdapter):
    """An implementation of an adapter holding multiple cookies"""

    _static_session: Optional[aiohttp.ClientSession] = None
    sessions: List[aiohttp.ClientSession]

    def __init__(
        self,
        cookies: Sequence[Mapping[str, str]] = None,
        authkey: str = None,
        *,
        lang: str = "en-us",
        debug: bool = False,
        cache: cache_.Cache = None,
    ) -> None:
        super().__init__(authkey=authkey, lang=lang, debug=debug, cache=cache)
        if cookies:
            self.cookies = cookies

    @property
    def static_session(self) -> aiohttp.ClientSession:
        """The currently chosen session"""
        if not self._static_session:
            self._static_session = aiohttp.ClientSession()

        return self._static_session

    @property
    def cookies(self) -> List[Mapping[str, str]]:
        """A list of all cookies"""
        return [{m.key: m.value for m in s.cookie_jar} for s in self.sessions]

    @cookies.setter
    def cookies(self, cookies: Sequence[Mapping[str, Any]]) -> None:
        self.set_cookies(cookies)

    def set_cookies(
        self,
        cookie_list: Union[Iterable[Union[Mapping[str, Any], str]], str],
        clear: bool = True,
    ) -> List[Mapping[str, str]]:
        """Set a list of cookies

        :param cookie_list: A list of cookies or a json file containing cookies
        :param clear: Whether to clear all of the previous cookies
        """
        if clear:
            self.sessions.clear()

        if isinstance(cookie_list, str):
            with open(cookie_list) as file:
                cookie_list = json_.load(file)

            if not isinstance(cookie_list, list):
                raise RuntimeError("Json file must contain a list of cookies")

        for cookies in cookie_list:
            session = aiohttp.ClientSession(cookies=SimpleCookie(cookies))
            self.sessions.append(session)

        return self.cookies

    async def close(self) -> None:
        tasks = [asyncio.create_task(session.close()) for session in self.sessions]
        if self._static_session:
            tasks.append(asyncio.create_task(self._static_session.close()))

        await asyncio.wait(tasks)

    @utils.handle_ratelimits()
    async def request(
        self,
        url: Union[str, URL],
        method: str = "GET",
        headers: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        headers = headers or {}
        headers["user-agent"] = self.USER_AGENT

        await self._request_hook(method, url, headers=headers, **kwargs)

        for session in self.sessions.copy():
            async with session.request(method, url, headers=headers, **kwargs) as r:
                r.raise_for_status()
                data = await r.json()

            if data["retcode"] == 0:
                return data["data"]

            try:
                errors.raise_for_retcode(data)
            except errors.TooManyRequests:
                # move the ratelimited session to the end to let the ratelimit wear off
                session = self.sessions.pop(0)
                self.sessions.append(session)

        # if we're here it means we used up all our sessions so we must handle that
        msg = "All cookies have hit their request limit of 30 accounts per day."
        raise errors.TooManyRequests({"retcode": 10101}, msg)

    async def request_webstatic(
        self,
        url: Union[str, URL],
        *,
        headers: Dict[str, Any] = None,
        cache: bool = True,
        **kwargs: Any,
    ) -> Any:
        url = URL(self.WEBSTATIC_URL).join(URL(url))

        if cache and (data := self.cache.get_from_static_cache(str(url))):
            return data

        headers = headers or {}
        headers["user-agent"] = self.USER_AGENT

        async with self.static_session.get(url, headers=headers, **kwargs) as r:
            r.raise_for_status()
            data = await r.json()

        if cache:
            self.cache.save_to_static_cache(str(url), data)

        return data
