"""Base battle chronicle component."""

import asyncio
import dataclasses
import typing
import warnings

from genshin import errors, models, types, utility
from genshin.client import cache, routes
from genshin.client.components import base
from genshin.client.manager import managers
from genshin.constants import GAME_LANGS
from genshin.models import hoyolab as hoyolab_models
from genshin.utility import deprecation

__all__ = ["BaseBattleChronicleClient"]


@dataclasses.dataclass(unsafe_hash=True)
class HoyolabCacheKey(cache.CacheKey):
    endpoint: str
    hoyolab_id: int
    lang: str


@dataclasses.dataclass(unsafe_hash=True)
class ChronicleCacheKey(cache.CacheKey):
    def __str__(self) -> str:
        return "chronicle" + ":" + super().__str__()

    game: types.Game
    endpoint: str
    uid: int
    lang: str
    params: tuple[typing.Any, ...] = ()


class BaseBattleChronicleClient(base.BaseClient):
    """Base battle chronicle component."""

    async def request_game_record(
        self,
        endpoint: str,
        *,
        lang: typing.Optional[str] = None,
        region: typing.Optional[types.Region] = None,
        game: typing.Optional[types.Game] = None,
        custom_route: typing.Optional[typing.Union[routes.Route, routes.InternationalRoute]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the game record endpoint."""
        game = game or self.default_game

        if isinstance(custom_route, routes.InternationalRoute):
            base_url = routes.CARD_WAPI_URL.get_url(region or self.region)
        elif isinstance(custom_route, routes.Route):
            base_url = custom_route.get_url()
        else:
            if game is None:
                raise RuntimeError("No default game set.")
            base_url = routes.RECORD_URL.get_url(region or self.region, game)

        if game is not None and (lang or self.lang) not in GAME_LANGS[game]:
            warnings.warn(f"Language '{lang or self.lang}' is not supported for {game.name}. Defaulting to 'en-us'.")
            lang = "en-us"

        url = base_url / endpoint

        update_task = asyncio.create_task(utility.update_characters_any(lang or self.lang, lenient=True))

        data = await self.request_hoyolab(url, lang=lang, region=region, **kwargs)

        try:
            await update_task
        except Exception as e:
            warnings.warn(f"Failed to update characters: {e!r}")

        return data

    async def get_record_cards(
        self, hoyolab_id: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> list[models.hoyolab.RecordCard]:
        """Get a user's record cards."""
        hoyolab_id = hoyolab_id or self._get_hoyolab_id()

        cache_key = cache.cache_key("records", hoyolab_id=hoyolab_id, lang=lang or self.lang)
        if not (data := await self.cache.get(cache_key)):
            data = await self.request_game_record(
                "getGameRecordCard", lang=lang, params=dict(uid=hoyolab_id), custom_route=routes.CARD_WAPI_URL
            )

            if data["list"]:
                await self.cache.set(cache_key, data)
            else:
                raise errors.DataNotPublic({"retcode": 10102})

        return [models.hoyolab.RecordCard(**card) for card in data["list"]]

    @deprecation.deprecated("get_record_cards")
    async def get_record_card(
        self, hoyolab_id: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> models.hoyolab.RecordCard:
        """Get a user's record card."""
        cards = await self.get_record_cards(hoyolab_id, lang=lang)
        return cards[0]

    @managers.no_multi
    async def update_settings(
        self,
        setting: types.IDOr[hoyolab_models.RecordCardSetting],
        on: bool,
        *,
        game: typing.Optional[types.Game] = None,
    ) -> None:
        """Update user settings.

        Setting IDs:
            1: Show your Battle Chronicle on your profile.
            2: Show your Character Details in the Battle Chronicle.
            3: Enable your Real-Time Notes. (only for Genshin Impact)
        """
        if game is None and int(setting) == 3:
            game = types.Game.GENSHIN

        if game is None:
            if self.default_game is None:
                raise RuntimeError("No default game set.")

            game = self.default_game

        game_id = {types.Game.HONKAI: 1, types.Game.GENSHIN: 2, types.Game.STARRAIL: 6, types.Game.ZZZ: 8}[game]

        await self.request_game_record(
            "changeDataSwitch",
            method="POST",
            data=dict(switch_id=int(setting), is_public=on, game_id=game_id),
            custom_route=routes.CARD_WAPI_URL,
        )

    @deprecation.deprecated("update_settings")
    async def set_visibility(self, public: bool, *, game: typing.Optional[types.Game] = None) -> None:
        """Set your data to public or private."""
        await self.update_settings(1, public, game=game)
