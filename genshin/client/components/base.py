"""Base ABC Client."""
import abc
import asyncio
import base64
import json
import logging
import os
import typing
import urllib.parse
import warnings

import aiohttp.typedefs
import yarl

from genshin import constants, errors, types, utility
from genshin.client import cache as client_cache
from genshin.client import routes
from genshin.client.manager import managers
from genshin.models import hoyolab as hoyolab_models
from genshin.models import model as base_model
from genshin.utility import concurrency, deprecation, ds

__all__ = ["BaseClient"]


class BaseClient(abc.ABC):
    """Base ABC Client."""

    __slots__ = ("cookie_manager", "cache", "_authkey", "_lang", "_region", "_default_game", "uids")

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"  # noqa: E501

    logger: logging.Logger = logging.getLogger(__name__)

    cookie_manager: managers.BaseCookieManager
    cache: client_cache.BaseCache
    _authkey: typing.Optional[str]
    _lang: str
    _region: types.Region
    _default_game: typing.Optional[types.Game]

    uids: typing.Dict[types.Game, int]
    _hoyolab_id: typing.Optional[int]

    def __init__(
        self,
        cookies: typing.Optional[managers.AnyCookieOrHeader] = None,
        *,
        authkey: typing.Optional[str] = None,
        lang: str = "en-us",
        region: types.Region = types.Region.OVERSEAS,
        proxy: typing.Optional[str] = None,
        game: typing.Optional[types.Game] = None,
        uid: typing.Optional[int] = None,
        hoyolab_id: typing.Optional[int] = None,
        cache: typing.Optional[client_cache.Cache] = None,
        debug: bool = False,
    ) -> None:
        self.cookie_manager = managers.BaseCookieManager.from_cookies(cookies)
        self.cache = cache or client_cache.StaticCache()

        self.authkey = authkey
        self.lang = lang
        self.region = region
        self.default_game = game
        self.debug = debug
        self.proxy = proxy
        self.uids = {}
        self.uid = uid
        self.hoyolab_id = hoyolab_id

    def __repr__(self) -> str:
        kwargs = dict(
            lang=self.lang,
            region=self.region.value,
            default_game=self.default_game and self.default_game.value,
            hoyolab_id=self.hoyolab_id,
            uid=self.default_game and self.uid,
            authkey=self.authkey and self.authkey[:12] + "...",
            proxy=self.proxy,
            debug=self.debug,
        )
        return f"<{type(self).__name__} {', '.join(f'{k}={v!r}' for k, v in kwargs.items() if v)}>"

    @property
    def hoyolab_id(self) -> typing.Optional[int]:
        """The logged-in user's hoyolab uid.

        Returns None if not found or not applicable.
        """
        return self._hoyolab_id or self.cookie_manager.user_id

    @hoyolab_id.setter
    def hoyolab_id(self, hoyolab_id: typing.Optional[int]) -> None:
        if self.cookie_manager.multi:
            raise RuntimeError("Cannot specify a hoyolab uid when using multiple cookies.")

        if self.cookie_manager.user_id and hoyolab_id and self.cookie_manager.user_id != hoyolab_id:
            raise ValueError("The provided hoyolab uid does not match the cookie id.")

        self._hoyolab_id = hoyolab_id

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
    def region(self, region: str) -> None:
        self._region = types.Region(region)

        if region == types.Region.CHINESE:
            self.lang = "zh-cn"

    @property
    def default_game(self) -> typing.Optional[types.Game]:
        """The default game."""
        return self._default_game

    @default_game.setter
    def default_game(self, game: typing.Optional[str]) -> None:
        self._default_game = types.Game(game) if game else None

    game = default_game

    @property
    def uid(self) -> typing.Optional[int]:
        """UID of the default game."""
        if self.default_game is None:
            if len(self.uids) != 1:
                return None

            (self.default_game,) = self.uids.keys()

        return self.uids.get(self.default_game)

    @uid.setter
    def uid(self, uid: typing.Optional[int]) -> None:
        if uid is None:
            self.uids.clear()
            return

        self._default_game = self._default_game or utility.recognize_game(uid, region=self.region)
        if self.default_game is None:
            raise RuntimeError("No default game set. Cannot set uid.")

        self.uids[self.default_game] = uid

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

    def set_cookies(self, cookies: typing.Optional[managers.AnyCookieOrHeader] = None, **kwargs: typing.Any) -> None:
        """Parse and set cookies."""
        if not bool(cookies) ^ bool(kwargs):
            raise TypeError("Cannot use both positional and keyword arguments at once")

        self.cookie_manager = managers.BaseCookieManager.from_cookies(cookies or kwargs)

    def set_browser_cookies(self, browser: typing.Optional[str] = None) -> None:
        """Extract cookies from your browser and set them as client cookies.

        Available browsers: chrome, chromium, opera, edge, firefox.
        """
        self.cookie_manager = managers.BaseCookieManager.from_browser_cookies(browser)

    def set_authkey(self, authkey: typing.Optional[str] = None) -> None:
        """Set an authkey for wish & transaction logs.

        Accepts an authkey, a url containing an authkey or a path towards a logfile.
        """
        if authkey is None or os.path.isfile(authkey):
            authkey = utility.get_authkey(authkey)
        else:
            authkey = utility.extract_authkey(authkey) or authkey

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
        **redis_kwargs: typing.Any,
    ) -> None:
        """Create and set a new redis cache."""
        import aioredis

        redis = aioredis.Redis.from_url(url, **redis_kwargs)  # pyright: ignore[reportUnknownMemberType]
        self.cache = client_cache.RedisCache(redis, ttl=ttl, static_ttl=static_ttl)

    @property
    def proxy(self) -> typing.Optional[str]:
        """Proxy for http requests."""
        if self.cookie_manager.proxy is None:
            return None

        return str(self.cookie_manager.proxy)

    @proxy.setter
    def proxy(self, proxy: typing.Optional[aiohttp.typedefs.StrOrURL]) -> None:
        self.cookie_manager.proxy = yarl.URL(proxy) if proxy else None

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
            value = await self.cache.get_static(static_cache)
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
            await self.cache.set_static(static_cache, response)

        return response

    async def request_webstatic(
        self,
        url: aiohttp.typedefs.StrOrURL,
        *,
        headers: typing.Optional[aiohttp.typedefs.LooseHeaders] = None,
        cache: typing.Any = None,
        region: types.Region = types.Region.OVERSEAS,
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Request a static json file."""
        if cache is not None:
            value = await self.cache.get_static(cache)
            if value is not None:
                return value

        url = routes.WEBSTATIC_URL.get_url(region).join(yarl.URL(url))

        headers = dict(headers or {})
        headers["User-Agent"] = self.USER_AGENT

        await self._request_hook("GET", url, headers=headers, **kwargs)

        async with self.cookie_manager.create_session() as session:
            async with session.get(url, headers=headers, proxy=self.proxy, **kwargs) as r:
                r.raise_for_status()
                data = await r.json()

        if cache is not None:
            await self.cache.set_static(cache, data)

        return data

    def _get_ds_headers(
        self,
        region:types.Region, data: typing.Any = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    ) -> typing.Dict:
        if region == types.Region.OVERSEAS:
            ds_headers = {
                "x-rpc-app_version": "1.5.0",
                "x-rpc-client_type": "4",
                "x-rpc-language": lang,
                "ds": ds.generate_dynamic_secret(),
            }
        elif region == types.Region.CHINESE:
            ds_headers = {
                "x-rpc-app_version": "2.11.1",
                "x-rpc-client_type": "5",
                "ds": ds.generate_cn_dynamic_secret(data, params),
            }
        else:
            raise TypeError(f"{region!r} is not a valid region.")
        return ds_headers

    async def request_bbs(
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
        """Make a request any bbs endpoint."""
        if lang is not None and lang not in constants.LANGS:
            raise ValueError(f"{lang} is not a valid language, must be one of: " + ", ".join(constants.LANGS))

        lang = lang or self.lang
        region = region or self.region

        url = routes.BBS_URL.get_url(region).join(yarl.URL(url))

        headers = dict(headers or {})
        headers.update(self._get_ds_headers(region, data, params))
        headers["Referer"] = str(routes.BBS_REFERER_URL.get_url(self.region))

        data = await self.request(url, method=method, params=params, data=data, headers=headers, **kwargs)
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

        headers = dict(headers or {})
        headers.update(self._get_ds_headers(region, data, params))

        data = await self.request(url, method=method, params=params, data=data, headers=headers, **kwargs)
        return data

    @managers.no_multi
    async def get_game_accounts(
        self,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[hoyolab_models.GenshinAccount]:
        """Get the game accounts of the currently logged-in user."""
        if self.hoyolab_id is None:
            warnings.warn("No hoyolab id set, caching may be unreliable.")

        data = await self.request_hoyolab(
            "binding/api/getUserGameRolesByCookie",
            lang=lang,
            cache=client_cache.cache_key("accounts", hoyolab_id=self.hoyolab_id),
        )
        return [hoyolab_models.GenshinAccount(**i) for i in data["list"]]

    @deprecation.deprecated("get_game_accounts")
    async def genshin_accounts(
        self,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[hoyolab_models.GenshinAccount]:
        """Get the genshin accounts of the currently logged-in user."""
        accounts = await self.get_game_accounts(lang=lang)
        return [account for account in accounts if account.game == types.Game.GENSHIN]

    async def _update_cached_uids(self) -> None:
        """Update cached fallback uids."""
        mixed_accounts = await self.get_game_accounts()

        game_accounts: typing.Dict[types.Game, typing.List[hoyolab_models.GenshinAccount]] = {}
        for account in mixed_accounts:
            if not isinstance(account.game, types.Game):  # pyright: ignore[reportUnnecessaryIsInstance]
                continue

            game_accounts.setdefault(account.game, []).append(account)

        self.uids = {game: max(accounts, key=lambda a: a.level).uid for game, accounts in game_accounts.items()}

        if len(self.uids) == 1 and self.default_game is None:
            (self.default_game,) = self.uids.keys()

    @concurrency.prevent_concurrency
    async def _get_uid(self, game: types.Game) -> int:
        """Get a cached fallback uid."""
        # TODO: use lock
        if uid := self.uids.get(game):
            return uid

        if self.cookie_manager.multi:
            raise RuntimeError("UID must be provided when using multi-cookie managers.")

        await self._update_cached_uids()

        if uid := self.uids.get(game):
            return uid

        raise errors.AccountNotFound(msg="No UID provided and account has no game account bound to it.")

    def _get_hoyolab_id(self) -> int:
        """Get a cached fallback hoyolab ID."""
        if self.hoyolab_id is not None:
            return self.hoyolab_id

        if self.cookie_manager.multi:
            raise RuntimeError("Hoyolab ID must be provided when using multi-cookie managers.")

        raise RuntimeError("No default hoyolab ID provided.")

    async def _fetch_mi18n(self, key: str, lang: str, *, force: bool = False) -> None:
        """Update mi18n for a single url."""
        if not force:
            if key in base_model.APIModel._mi18n:
                return

        base_model.APIModel._mi18n[key] = {}

        url = routes.MI18N[key]
        cache_key = client_cache.cache_key("mi18n", mi18n=key, lang=lang)

        data = await self.request_webstatic(url.format(lang=lang), cache=cache_key)
        for k, v in data.items():
            actual_key = str.lower(key + "/" + k)
            base_model.APIModel._mi18n.setdefault(actual_key, {})[lang] = v

    async def update_mi18n(self, langs: typing.Iterable[str] = constants.LANGS, *, force: bool = False) -> None:
        """Fetch mi18n for partially localized endpoints."""
        if not force:
            if base_model.APIModel._mi18n:
                return

        langs = tuple(langs)

        coros: typing.List[typing.Awaitable[None]] = []
        for key in routes.MI18N:
            for lang in langs:
                coros.append(self._fetch_mi18n(key, lang, force=force))

        await asyncio.gather(*coros)
