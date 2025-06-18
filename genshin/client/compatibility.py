"""Reverse-compatibility layer for previous versions."""

from __future__ import annotations

import typing

import aiohttp

from genshin import models, types
from genshin.utility import deprecation

from . import clients

__all__ = ["ChineseClient", "ChineseMultiCookieClient", "GenshinClient", "MultiCookieClient"]


class GenshinClient(clients.Client):
    """A simple http client for genshin endpoints.

    !!! warning
        This class is deprecated and will be removed in the following version.
        Use `Client()` instead.
    """

    def __init__(
        self,
        cookies: typing.Optional[typing.Any] = None,
        authkey: typing.Optional[str] = None,
        *,
        lang: types.Lang = "en-us",
        region: types.Region = types.Region.OVERSEAS,
        debug: bool = False,
    ) -> None:
        deprecation.warn_deprecated(self.__class__, alternative="Client")
        super().__init__(
            cookies=cookies,
            authkey=authkey,
            lang=lang,
            region=region,
            game=types.Game.GENSHIN,
            debug=debug,
        )

    @property
    def session(self) -> aiohttp.ClientSession:
        """The current client session, created when needed."""
        deprecation.warn_deprecated(self.__class__.session)
        return self.cookie_manager.create_session()

    @property
    def cookies(self) -> typing.Mapping[str, str]:
        """The cookie jar belonging to the current session."""
        deprecation.warn_deprecated(self.__class__.cookies, alternative="cookie_manager")
        return getattr(self.cookie_manager, "cookies")

    @cookies.setter
    def cookies(self, cookies: typing.Mapping[str, typing.Any]) -> None:
        deprecation.warn_deprecated("Setting cookies with GenshinClient.cookies", alternative="set_cookies")
        setattr(self.cookie_manager, "cookies", cookies)

    @property
    def uid(self) -> typing.Optional[int]:
        deprecation.warn_deprecated(self.__class__.uid, alternative="Client.uids[genshin.Game.GENSHIN]")
        return self.uids[types.Game.GENSHIN]

    @uid.setter
    def uid(self, uid: typing.Optional[int]) -> None:
        deprecation.warn_deprecated(
            "Setting uid with GenshinClient.uid",
            alternative="Client.uids[genshin.Game.GENSHIN]",
        )
        if uid is not None:
            self.uids[types.Game.GENSHIN] = uid

    @deprecation.deprecated()
    async def __aenter__(self) -> GenshinClient:
        return self

    async def __aexit__(self, *exc_info: typing.Any) -> None:
        pass

    @deprecation.deprecated("get_partial_genshin_user")
    async def get_partial_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.PartialGenshinUserStats:
        """Get partial genshin user without character equipment."""
        return await self.get_partial_genshin_user(uid, lang=lang)

    @deprecation.deprecated("get_genshin_characters")
    async def get_characters(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.Character]:
        """Get genshin user characters."""
        return await self.get_genshin_characters(uid, lang=lang)

    @deprecation.deprecated("get_genshin_user")
    async def get_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.GenshinUserStats:
        """Get genshin user."""
        return await self.get_genshin_user(uid, lang=lang)

    @deprecation.deprecated("get_full_genshin_user")
    async def get_full_user(
        self,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.FullGenshinUserStats:
        """Get a user with all their possible data."""
        return await self.get_full_genshin_user(uid, lang=lang)


class ChineseClient(GenshinClient):
    """A Genshin Client for chinese endpoints.

    !!! warning
        This class is deprecated and will be removed in the following version.
        Use `Client(region=genshin.Region.CHINESE)` instead.
    """

    def __init__(
        self,
        cookies: typing.Optional[typing.Mapping[str, str]] = None,
        authkey: typing.Optional[str] = None,
        *,
        lang: types.Lang = "zh-cn",
        debug: bool = False,
    ) -> None:
        super().__init__(
            cookies=cookies,
            authkey=authkey,
            lang=lang,
            region=types.Region.CHINESE,
            debug=debug,
        )


class MultiCookieClient(GenshinClient):
    """A Genshin Client which allows setting multiple cookies.

    !!! warning
        This class is deprecated and will be removed in the following version.
        Use `Client(cookies=[...])` instead.
    """

    def __init__(
        self,
        cookie_list: typing.Optional[typing.Sequence[typing.Mapping[str, str]]] = None,
        *,
        lang: types.Lang = "en-us",
        debug: bool = False,
    ) -> None:
        super().__init__(
            cookies=cookie_list,
            lang=lang,
            debug=debug,
        )


class ChineseMultiCookieClient(GenshinClient):
    """A Genshin Client for chinese endpoints which allows setting multiple cookies.

    !!! warning
        This class is deprecated and will be removed in the following version.
        Use `Client(cookies=[...], region=genshin.Region.CHINESE)` instead.
    """

    def __init__(
        self,
        cookie_list: typing.Optional[typing.Sequence[typing.Mapping[str, str]]] = None,
        *,
        lang: types.Lang = "en-us",
        debug: bool = False,
    ) -> None:
        super().__init__(
            cookies=cookie_list,
            lang=lang,
            region=types.Region.CHINESE,
            debug=debug,
        )
