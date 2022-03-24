"""Base ABC Client."""
import abc
import base64
import json
import logging
import os
import typing
import urllib.parse

import aiohttp.typedefs
import yarl

from genshin import constants, errors, types
from genshin.client import cache as client_cache
from genshin.client import manager, routes
from genshin.models import hoyolab as hoyolab_models
from genshin.utility import ds
from genshin.utility import genshin as genshin_utility

__all__ = ["BaseClient"]


class BaseClient(abc.ABC):
    """Base ABC Client."""

    __slots__ = ("cookie_manager", "cache", "_authkey", "_lang", "_region", "_default_game", "uids")

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"  # noqa: E501

    logger: logging.Logger = logging.getLogger(__name__)

    cookie_manager: manager.AbstractCookieManager
    cache: client_cache.BaseCache
    _authkey: typing.Optional[str]
    _lang: str
    _region: types.Region
    _default_game: typing.Optional[types.Game]

    uids: typing.Dict[types.Game, int]

    def __init__(
        self,
        cookies: typing.Optional[manager.AnyCookieOrHeader] = None,
        *,
        authkey: typing.Optional[str] = None,
        lang: str = "en-us",
        region: types.Region = types.Region.OVERSEAS,
        game: typing.Optional[types.Game] = None,
        cache: typing.Optional[client_cache.Cache] = None,
        debug: bool = False,
    ) -> None:
        self.cookie_manager = manager.AbstractCookieManager.from_cookies(cookies)
        self.cache = cache or client_cache.NOOPCache()

        self.authkey = authkey
        self.lang = lang
        self.region = region
        self.default_game = game
        self.debug = debug

        self.uids = {}

    def __repr__(self) -> str:
        kwargs = dict(
            lang=self.lang,
            region=self.region.value,
            default_game=self.default_game and self.default_game.value,
            hoyolab_uid=self.hoyolab_uid,
            authkey=self.authkey and self.authkey[:12] + "...",
            debug=self.debug,
        )
        return f"<{type(self).__name__} {', '.join(f'{k}={v!r}' for k, v in kwargs.items() if v)}>"

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
    def region(self) -> types.Region:
        """The default region."""
        return self._region

    @region.setter
    def region(self, region: types.Region) -> None:
        self._region = region

        if region is types.Region.CHINESE:
            self.lang = "zh-cn"

    @property
    def default_game(self) -> typing.Optional[types.Game]:
        """The default game."""
        return self._default_game

    @default_game.setter
    def default_game(self, game: typing.Optional[types.Game]) -> None:
        self._default_game = game

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

        self.cookie_manager = manager.AbstractCookieManager.from_cookies(cookies or kwargs)

    def set_browser_cookies(self, browser: typing.Optional[str] = None) -> None:
        """Extract cookies from your browser and set them as client cookies.

        Available browsers: chrome, chromium, opera, edge, firefox.
        """
        self.cookie_manager = manager.AbstractCookieManager.from_browser_cookies(browser)

    def set_authkey(self, authkey: typing.Optional[str] = None) -> None:
        """Set an authkey for wish & transaction logs.

        Accepts an authkey, a url containing an authkey or a path towards a logfile.
        """
        if authkey is None or os.path.isfile(authkey):
            authkey = genshin_utility.get_authkey(authkey)
        else:
            authkey = genshin_utility.extract_authkey(authkey) or authkey

        self.authkey = authkey

    def set_cache(
        self,
        maxsize: int = 1024,
        *,
        ttl: int = client_cache.HOUR,
        static_ttl: int = client_cache.DAY,
    ) -> None:
        """Create and set a new cache."""
        self.cache = client_cache.Cache(maxsize, ttl=ttl, static_ttl=static_ttl)

    def set_redis_cache(
        self,
        url: str,
        *,
        ttl: int = client_cache.HOUR,
        static_ttl: int = client_cache.DAY,
        **kwargs: typing.Any,
    ) -> None:
        """Create and set a new redis cache."""
        import aioredis

        redis = aioredis.Redis.from_url(url, **kwargs)  # pyright: ignore[reportUnknownMemberType]
        self.cache = client_cache.RedisCache(redis, ttl=ttl, static_ttl=static_ttl)

    async def _request_hook(
        self,
        method: str,
        url: aiohttp.typedefs.StrOrURL,
        *,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        data: typing.Any = None,
        **kwargs: typing.Any,
    ) -> None:
        """Perform an action before a request.

        Debug logging by default.
        """
        url = yarl.URL(url)
        if params:
            params = {k: v for k, v in params.items() if k != "authkey"}
            url = url.update_query(params)

        if data:
            self.logger.debug("%s %s\n%s", method, url, json.dumps(data, separators=(",", ":")))
        else:
            self.logger.debug("%s %s", method, url)

    async def request(
        self,
        url: aiohttp.typedefs.StrOrURL,
        *,
        method: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        data: typing.Any = None,
        headers: typing.Optional[aiohttp.typedefs.LooseHeaders] = None,
        cache: typing.Any = None,
        static_cache: typing.Any = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request and return a parsed json response."""
        if cache is not None:
            value = await self.cache.get(cache)
            if value is not None:
                return value
        elif static_cache is not None:
            value = await self.cache.get_static(cache)
            if value is not None:
                return value

        # actual request

        headers = dict(headers or {})
        headers["User-Agent"] = self.USER_AGENT

        if method is None:
            method = "POST" if data else "GET"

        if "json" in kwargs:
            raise TypeError("Use data instead of json in request.")

        await self._request_hook(method, url, params=params, data=data, headers=headers, **kwargs)

        response = await self.cookie_manager.request(
            url,
            method=method,
            params=params,
            json=data,
            headers=headers,
            **kwargs,
        )

        # cache

        if cache is not None:
            await self.cache.set(cache, response)
        elif static_cache is not None:
            await self.cache.set_static(cache, response)

        return response

    async def request_webstatic(
        self,
        url: aiohttp.typedefs.StrOrURL,
        *,
        headers: typing.Optional[aiohttp.typedefs.LooseHeaders] = None,
        cache: typing.Any = None,
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Request a static json file."""
        if cache is not None:
            value = await self.cache.get(cache)
            if value is not None:
                return value

        url = routes.WEBSTATIC_URL.get_url().join(yarl.URL(url))

        headers = dict(headers or {})
        headers["User-Agent"] = self.USER_AGENT

        async with self.cookie_manager.create_session() as session:
            async with session.get(url, headers=headers, **kwargs) as r:
                r.raise_for_status()
                data = await r.json()

        if cache is not None:
            await self.cache.set(cache, data)

        return data

    async def request_hoyolab(
        self,
        url: aiohttp.typedefs.StrOrURL,
        *,
        lang: typing.Optional[str] = None,
        region: typing.Optional[types.Region] = None,
        method: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        data: typing.Any = None,
        headers: typing.Optional[aiohttp.typedefs.LooseHeaders] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request any hoyolab endpoint."""
        if lang is not None and lang not in constants.LANGS:
            raise ValueError(f"{lang} is not a valid language, must be one of: " + ", ".join(constants.LANGS))

        lang = lang or self.lang
        region = region or self.region

        url = routes.TAKUMI_URL.get_url(region).join(yarl.URL(url))

        if region is types.Region.OVERSEAS:
            headers = {
                "x-rpc-app_version": "1.5.0",
                "x-rpc-client_type": "4",
                "x-rpc-language": lang,
                "ds": ds.generate_dynamic_secret(),
            }
        elif region is types.Region.CHINESE:
            headers = {
                "x-rpc-app_version": "2.11.1",
                "x-rpc-client_type": "5",
                "ds": ds.generate_cn_dynamic_secret(data, params),
            }
        else:
            raise TypeError(f"{region!r} is not a valid region.")

        data = await self.request(url, method=method, params=params, data=data, headers=headers, **kwargs)
        return data

    @manager.no_multi
    async def get_game_accounts(
        self,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[hoyolab_models.GenshinAccount]:
        """Get the game accounts of the currently logged-in user."""
        data = await self.request_hoyolab(
            "binding/api/getUserGameRolesByCookie",
            lang=lang,
            cache=client_cache.UniqueCacheKey("accounts"),
        )
        return [hoyolab_models.GenshinAccount(**i) for i in data["list"]]

    async def _update_cached_uids(self) -> None:
        """Update cached fallback uids."""
        mixed_accounts = await self.get_game_accounts()

        game_accounts: typing.Dict[types.Game, typing.List[hoyolab_models.GenshinAccount]] = {}
        for account in mixed_accounts:
            game_accounts.setdefault(account.game, []).append(account)

        self.uids = {game: max(accounts, key=lambda a: a.level).uid for game, accounts in game_accounts.items()}

    async def _get_uid(self, game: types.Game) -> int:
        """Get a cached fallback uid."""
        if uid := self.uids.get(game):
            return uid

        if self.cookie_manager.multi:
            raise RuntimeError("UID must be provided when using multi-cookie managers.")

        await self._update_cached_uids()

        if uid := self.uids.get(game):
            return uid

        raise errors.AccountNotFound(msg="No UID provided and account has no game account bound to it.")
