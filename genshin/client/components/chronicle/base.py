"""Base battle chronicle component."""

import typing

from genshin import errors, models, types
from genshin.client import routes
from genshin.client.components import base
from genshin.utility import deprecation

__all__ = ["BaseBattleChronicleClient"]


class BaseBattleChronicleClient(base.BaseClient):
    """Base battle chronicle component."""

    async def request_game_record(
        self,
        endpoint: str,
        *,
        lang: typing.Optional[str] = None,
        region: typing.Optional[types.Region] = None,
        game: typing.Optional[types.Game] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the game record endpoint."""
        base_url = routes.RECORD_URL.get_url(region or self.region)

        if game:
            base_url = base_url / game.value / "api"

        url = base_url / endpoint

        return await self.request_hoyolab(url, lang=lang, region=region, **kwargs)

    async def get_record_cards(
        self,
        hoyolab_uid: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.List[models.hoyolab.RecordCard]:
        """Get a user's record cards."""
        data = await self.request_game_record(
            "card/wapi/getGameRecordCard",
            lang=lang,
            params=dict(uid=hoyolab_uid or self.cookie_manager.get_user_id()),
        )

        cards = data["list"]
        if not cards:
            raise errors.DataNotPublic({"retcode": 10102})

        return [models.hoyolab.RecordCard(**card) for card in cards]

    @deprecation.deprecated(alternative="get_record_cards")
    async def get_record_card(
        self,
        hoyolab_uid: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.hoyolab.RecordCard:
        """Get a user's record card."""
        cards = await self.get_record_cards(hoyolab_uid, lang=lang)
        return cards[0]

    async def set_visibility(self, public: bool, game: typing.Optional[types.Game] = None) -> None:
        """Set your data to public or private."""
        if game is None:
            if self.default_game is None:
                raise RuntimeError("No default game set.")

            game = self.default_game

        game_id = {types.Game.HONKAI: 1, types.Game.GENSHIN: 2}[game]

        await self.request_game_record(
            "genshin/wapi/publishGameRecord",
            method="POST",
            json=dict(is_public=public, game_id=game_id),
        )
