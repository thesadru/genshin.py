"""Daily reward component."""

import asyncio
import datetime
import functools
import typing
import uuid

import aiohttp.typedefs

from genshin import constants, paginators, types
from genshin.client import cache, routes
from genshin.client.components import base
from genshin.client.manager import managers
from genshin.models.genshin import daily as models
from genshin.utility import ds as ds_utility

__all__ = ["DailyRewardClient"]


class DailyRewardClient(base.BaseClient):
    """Daily reward component."""

    @managers.no_multi
    async def request_daily_reward(
        self,
        endpoint: str,
        *,
        game: typing.Optional[types.Game] = None,
        method: str = "GET",
        lang: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        headers: typing.Optional[aiohttp.typedefs.LooseHeaders] = None,
        challenge: typing.Optional[typing.Mapping[str, str]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the daily reward endpoint."""
        params = dict(params or {})
        headers = base.parse_loose_headers(headers)

        if game is None:
            if self.default_game is None:
                raise RuntimeError("No default game set.")

            game = self.default_game

        base_url = routes.REWARD_URL.get_url(self.region, game)
        url = (base_url / endpoint).update_query(**base_url.query)

        if game is types.Game.GENSHIN:
            headers["x-rpc-signgame"] = "hk4e"
        elif game is types.Game.STARRAIL:
            headers["x-rpc-signgame"] = "hkrpg"
        elif game is types.Game.ZZZ:
            headers["x-rpc-signgame"] = "zzz"

        if self.region == types.Region.OVERSEAS:
            params["lang"] = lang or self.lang
            headers["referer"] = "https://act.hoyolab.com/"

        elif self.region == types.Region.CHINESE:
            account = await self._get_account(game)

            params["uid"] = account.uid
            params["region"] = account.server

            # These headers are optional but left here because they might affect geetest trigger rate
            headers["x-rpc-app_version"] = "2.70.1"
            headers["x-rpc-client_type"] = "5"
            headers["x-rpc-device_id"] = str(uuid.uuid4())
            headers["x-rpc-sys_version"] = "12"
            headers["x-rpc-platform"] = "android"
            headers["x-rpc-channel"] = "miyousheluodi"
            headers["x-rpc-device_model"] = str(self.hoyolab_id) or ""

            headers["ds"] = ds_utility.generate_dynamic_secret(constants.DS_SALT["cn_signin"])

        if challenge:
            headers["x-rpc-challenge"] = challenge["challenge"]
            headers["x-rpc-seccode"] = challenge["seccode"]
            headers["x-rpc-validate"] = challenge["validate"]

        return await self.request(url, method=method, params=params, headers=headers, **kwargs)

    async def get_reward_info(
        self,
        *,
        game: typing.Optional[types.Game] = None,
        lang: typing.Optional[str] = None,
    ) -> models.DailyRewardInfo:
        """Get the daily reward info for the current user."""
        data = await self.request_daily_reward("info", game=game, lang=lang)
        return models.DailyRewardInfo(data["is_sign"], data["total_sign_day"])

    async def get_monthly_rewards(
        self,
        *,
        game: typing.Optional[types.Game] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.DailyReward]:
        """Get a list of all availible rewards for the current month."""
        data = await self.request_daily_reward(
            "home",
            game=game,
            static_cache=cache.cache_key(
                "rewards",
                month=datetime.datetime.now(constants.CN_TIMEZONE).month,
                region=self.region,
                game=typing.cast("types.Game", game or self.default_game),  # (resolved later)
                lang=lang or self.lang,
            ),
        )
        return [models.DailyReward(**i) for i in data["awards"]]

    async def _get_claimed_rewards_page(
        self,
        page: int,
        *,
        game: typing.Optional[types.Game] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.ClaimedDailyReward]:
        """Get a single page of claimed rewards for the current user."""
        data = await self.request_daily_reward("award", params=dict(current_page=page), game=game, lang=lang)
        return [models.ClaimedDailyReward(**i) for i in data["list"]]

    def claimed_rewards(
        self,
        *,
        limit: typing.Optional[int] = None,
        game: typing.Optional[types.Game] = None,
        lang: typing.Optional[str] = None,
    ) -> paginators.Paginator[models.ClaimedDailyReward]:
        """Get all claimed rewards for the current user."""
        return paginators.PagedPaginator(
            functools.partial(
                self._get_claimed_rewards_page,
                game=game,
                lang=lang,
            ),
            limit=limit,
            page_size=10,
        )

    @typing.overload
    async def claim_daily_reward(  # noqa: D102 missing docstring in overload?
        self,
        *,
        game: typing.Optional[types.Game] = None,
        lang: typing.Optional[str] = None,
        reward: typing.Literal[True] = ...,
        challenge: typing.Optional[typing.Mapping[str, str]] = None,
    ) -> models.DailyReward: ...

    @typing.overload
    async def claim_daily_reward(  # noqa: D102 missing docstring in overload?
        self,
        *,
        game: typing.Optional[types.Game] = None,
        lang: typing.Optional[str] = None,
        reward: typing.Literal[False],
        challenge: typing.Optional[typing.Mapping[str, str]] = None,
    ) -> None: ...

    async def claim_daily_reward(
        self,
        *,
        game: typing.Optional[types.Game] = None,
        lang: typing.Optional[str] = None,
        reward: bool = True,
        challenge: typing.Optional[typing.Mapping[str, str]] = None,
    ) -> typing.Optional[models.DailyReward]:
        """Signs into hoyolab and claims the daily reward."""
        await self.request_daily_reward("sign", method="POST", game=game, lang=lang, challenge=challenge)

        if not reward:
            return None

        info, rewards = await asyncio.gather(
            self.get_reward_info(game=game, lang=lang),
            self.get_monthly_rewards(game=game, lang=lang),
        )
        return rewards[info.claimed_rewards - 1]
