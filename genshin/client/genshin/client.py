from __future__ import annotations

import abc
import asyncio
import base64
import functools
import json as json_
import logging
import os
import uuid
import warnings
from datetime import datetime
from http.cookies import SimpleCookie
from typing import *
from urllib.parse import unquote

import aiohttp
from yarl import URL

from genshin import errors
from genshin import models as base_models
from genshin import paginators, utils
from genshin.constants import CHARACTER_NAMES, LANGS
from genshin.models import genshin as gmodels

from .. import base  # TODO: Normalize import

CallableT = TypeVar("CallableT", bound=Callable[..., Any])


@property
@abc.abstractmethod
def _abc_str(self) -> str:
    ...


abc_str = cast(str, _abc_str)


def ensure_std_adapter(func: CallableT) -> CallableT:
    def wrapper(self: BaseGenshinClient, *args: Any, **kwargs: Any) -> Any:
        if isinstance(self, base.MultiCookieAdapter):
            raise AttributeError(f"'{type(self)}' object has no method '{func.__name__}'")

        return func(self, *args, **kwargs)

    return functools.update_wrapper(wrapper, func)  # type: ignore


class BaseGenshinClient(base.BaseAdapter):
    DS_SALT: str = abc_str
    ACT_ID: str = abc_str

    TAKUMI_URL: str = abc_str
    RECORD_URL: str = abc_str
    INFO_LEDGER_URL: str = abc_str
    DETAIL_LEDGER_URL: str = abc_str
    CALCULATOR_URL: str = abc_str
    REWARD_URL: str = abc_str
    GACHA_INFO_URL: str = abc_str
    YSULOG_URL: str = abc_str
    MAP_URL: str = abc_str
    STATIC_MAP_URL: str = abc_str

    async def request_hoyolab(
        self,
        endpoint: Union[str, URL],
        *,
        method: str = "GET",
        lang: str = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards misc hoyolabs api

        Community related data
        """
        if not self.cookies:
            raise RuntimeError("No cookies provided")
        if lang not in LANGS and lang is not None:
            raise ValueError(f"{lang} is not a valid language, must be one of: " + ", ".join(LANGS))

        url = URL(self.TAKUMI_URL).join(URL(endpoint))

        headers = {
            "x-rpc-app_version": "1.5.0",
            "x-rpc-client_type": "4",
            "x-rpc-language": lang or self.lang,
            "ds": utils.generate_dynamic_secret(self.DS_SALT),
        }

        data = await self.request(url, method=method, headers=headers, **kwargs)

        return data

    async def request_game_record(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        cache: Tuple[Any, ...] = None,
        cache_check: Callable[[Any], bool] = None,
        **kwargs: Any,
    ):
        """Make a request towards the game record endpoint

        User stats related data
        """
        # this is simply just an alias for shorter request endpoints
        url = URL(self.RECORD_URL).join(URL(endpoint))

        return await self.request_hoyolab(url, method=method, cache=cache, cache_check=cache_check, **kwargs)

    async def request_ledger(
        self,
        uid: int = None,
        detail: bool = False,
        *,
        month: int = None,
        lang: str = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make a request towards the ys ledger endpoint

        Traveler's diary related data
        """
        params = params or {}

        url = URL(self.DETAIL_LEDGER_URL if detail else self.INFO_LEDGER_URL)

        params.update(await self._complete_uid(uid))
        params["month"] = month or datetime.now().month
        params["lang"] = lang or self.lang

        return await self.request(url, params=params)

    async def request_calculator(
        self,
        endpoint: str,
        *,
        method: str = "POST",
        lang: str = None,
        params: Dict[str, Any] = None,
        json: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the calculator endpoint

        Calculator database and resource calculation
        """
        params = params or {}
        json = json or {}

        if not self.cookies:
            raise RuntimeError("No cookies provided")

        url = URL(self.CALCULATOR_URL).join(URL(endpoint))

        if method == "GET":
            params["lang"] = lang or self.lang
            json = None
        else:
            json["lang"] = lang or self.lang

        return await self.request(url, method=method, params=params, json=json, **kwargs)

    async def request_daily_reward(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: str = None,
        params: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the daily reward endpoint

        Daily reward claiming and history
        """
        params = params or {}

        if not self.cookies:
            raise RuntimeError("No cookies provided")

        url = URL(self.REWARD_URL).join(URL(endpoint))

        params["lang"] = lang or self.lang
        params["act_id"] = self.ACT_ID

        return await self.request(url, method=method, params=params, **kwargs)

    async def request_gacha_info(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: str = None,
        authkey: Optional[str] = None,
        params: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the game info endpoint

        Wish history related data
        """
        params = params or {}
        authkey = authkey or self.authkey

        if authkey is None:
            raise RuntimeError("No authkey provided")

        base_url = URL(self.GACHA_INFO_URL)
        url = base_url.join(URL(endpoint))

        params["authkey_ver"] = 1
        params["authkey"] = unquote(authkey)
        params["lang"] = utils.create_short_lang_code(lang or self.lang)

        return await self.request(url, method=method, params=params, **kwargs)

    async def request_transaction(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: str = None,
        authkey: Optional[str] = None,
        params: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request towards the transaction log endpoint

        Transaction related data
        """
        params = params or {}
        authkey = authkey or self.authkey

        if authkey is None:
            raise RuntimeError("No authkey provided")

        base_url = URL(self.YSULOG_URL)
        url = base_url.join(URL(endpoint))

        params["authkey_ver"] = 1
        params["sign_type"] = 2
        params["authkey"] = unquote(authkey)
        params["lang"] = utils.create_short_lang_code(lang or self.lang)

        return await self.request(url, method=method, params=params, **kwargs)

    @ensure_std_adapter
    async def genshin_accounts(self, *, lang: str = None) -> List[gmodels.GenshinAccount]:
        """Get the genshin accounts of the currently logged-in user

        :params lang: The language to use
        """
        data = await self.request_hoyolab(
            "binding/api/getUserGameRolesByCookie",
            lang=lang,
        )
        return [gmodels.GenshinAccount(**i) for i in data["list"]]

    async def search_users(self, keyword: str, *, lang: str = None) -> List[base_models.SearchUser]:
        """Search hoyolab users

        :param keyword: The keyword to search with
        :params lang: The language to use
        """
        data = await self.request_hoyolab(
            "community/search/wapi/search/user",
            lang=lang,
            params=dict(keyword=keyword, page_size=20),
            cache=("search", keyword),
        )
        return [base_models.SearchUser(**i["user"]) for i in data["list"]]

    async def set_visibility(self, public: bool) -> None:
        """Sets your data to public or private.

        :param public: Whether the data should now be public
        """
        await self.request_game_record(
            "genshin/wapi/publishGameRecord",
            method="POST",
            json=dict(is_public=public, game_id=2),
        )

    async def get_recommended_users(self, *, limit: int = 200) -> List[base_models.SearchUser]:
        """Get a list of recommended active users

        :param limit: The maximum amount of users to return
        """
        data = await self.request_hoyolab(
            "community/user/wapi/recommendActive",
            params=dict(page_size=limit),
        )
        return [base_models.SearchUser(**i["user"]) for i in data["list"]]

    @ensure_std_adapter
    async def redeem_code(self, code: str, uid: int = None, *, lang: str = None) -> None:
        """Redeems a gift code for the current user

        :param code: The code to redeem
        :param uid: The specific uid to redeem for
        :param lang: The language to use
        """
        # do note that this endpoint is very quirky, can't really make this pretty
        if uid is not None:
            server = utils.recognize_server(uid)
            lang = utils.create_short_lang_code(lang or self.lang)
            await self.request(
                "https://hk4e-api-os.mihoyo.com/common/apicdkey/api/webExchangeCdkey",
                params=dict(
                    uid=uid,
                    region=server,
                    cdkey=code,
                    game_biz="hk4e_global",
                    lang=lang,
                ),
            )
            return

        accounts = [a for a in await self.genshin_accounts() if a.level >= 10]

        for i, account in enumerate(accounts):
            # there's a ratelimit of 1 request every 5 seconds
            if i:
                await asyncio.sleep(5)

            await self.redeem_code(code, account.uid, lang=lang)

    # GAME RECORD:

    async def __fetch_user(self, uid: int, lang: str = None) -> Dict[str, Any]:
        """Low-level http method for fetching the game record index"""
        server = utils.recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/index",
            lang=lang,
            params=dict(server=server, role_id=uid),
            cache=("user", uid),
        )
        return data

    async def __fetch_characters(
        self, uid: int, character_ids: List[int], individual: bool = False, lang: str = None
    ) -> List[Dict[str, Any]]:
        """Low-level http method for fetching the game record characters

        Caching with characters is optimized
        """
        if not character_ids:
            return []

        character_ids = sorted(set(character_ids))

        if individual:
            sem = asyncio.Semaphore(5)

            async def _helper(character_id: int):
                async with sem:
                    c = await self.__fetch_characters(uid, [character_id], lang=lang)
                return c[0]

            data = await asyncio.gather(*map(_helper, character_ids), return_exceptions=True)
            return [i for i in data if not isinstance(i, BaseException)]

        # try to get all the characters from the cache
        coros = [
            asyncio.create_task(self._check_cache(("character", uid, charid), lang=lang)) for charid in character_ids
        ]
        characters = await asyncio.gather(*coros)
        if all(characters):
            # mypy bug - all does not function as a type guard
            return sorted(characters, key=lambda c: c["id"])  # type: ignore

        server = utils.recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/character",
            method="POST",
            lang=lang,
            json=dict(character_ids=character_ids, role_id=uid, server=server),
        )

        # update the cache one by one
        characters = data["avatars"]
        coros = [asyncio.create_task(self._update_cache(char, ("character", uid, char["id"]))) for char in characters]
        await asyncio.wait(coros)

        return sorted(characters, key=lambda c: c["id"])

    async def get_record_card(self, hoyolab_uid: int = None, *, lang: str = None) -> gmodels.RecordCard:
        """Get a user's record card

        :param hoyolab_uid: A hoyolab uid
        :param lang: The language to use
        """
        data = await self.request_game_record(
            "card/wapi/getGameRecordCard",
            lang=lang,
            params=dict(uid=hoyolab_uid or self.hoyolab_uid),
            cache=("record", hoyolab_uid),
            cache_check=lambda data: len(data["list"]) > 0,
        )
        cards = data["list"]
        if not cards:
            raise errors.DataNotPublic({"retcode": 10102})

        return gmodels.RecordCard(**cards[0])

    async def get_user(
        self,
        uid: int,
        *,
        character_ids: List[int] = None,
        all_characters: bool = False,
        lang: str = None,
    ) -> gmodels.UserStats:
        """Get a user's stats and characters

        :param uid: A Genshin uid
        :param character_ids: The ids of characters you want to fetch
        :param all_characters: Whether to get every single character a user has. Discouraged.
        :param lang: The language to use
        """
        # TODO: Optimize all_characters
        if character_ids is None:
            character_ids = list(CHARACTER_NAMES) if all_characters else []

        data = await self.__fetch_user(uid, lang=lang)
        character_ids = [char["id"] for char in data["avatars"]] + character_ids
        data["avatars"] = await self.__fetch_characters(
            uid,
            character_ids,
            individual=all_characters,
            lang=lang,
        )

        return gmodels.UserStats(**data)

    async def get_partial_user(self, uid: int, *, lang: str = None) -> gmodels.PartialUserStats:
        """Helper function to get a user without any equipment

        :param uid: A Genshin uid
        :param lang: The language to use
        """
        data = await self.__fetch_user(uid, lang=lang)
        return gmodels.PartialUserStats(**data)

    async def get_characters(
        self,
        uid: int,
        character_ids: List[int],
        *,
        individual: bool = False,
        lang: str = None,
    ) -> List[gmodels.Character]:
        """Helper function to fetch characters from just their ids

        :param uid: A Genshin uid
        :param character_ids: The ids of characters you want to fetch
        :param individual: Whether to get all characters individual in order to return only the ones the user has
        :param lang: The language to use
        """
        data = await self.__fetch_characters(uid, character_ids, individual=individual, lang=lang)
        return [gmodels.Character(**i) for i in data]

    async def get_spiral_abyss(self, uid: int, *, previous: bool = False, lang: str = None) -> gmodels.SpiralAbyss:
        """Get spiral abyss runs

        :param uid: A Genshin uid
        :param previous: Whether to get the record of the previous spiral abyss
        :param lang: The language to use
        """
        server = utils.recognize_server(uid)
        schedule_type = 2 if previous else 1
        data = await self.request_game_record(
            "genshin/api/spiralAbyss",
            lang=lang,
            params=dict(role_id=uid, server=server, schedule_type=schedule_type),
            cache=("abyss", uid, schedule_type),
        )
        return gmodels.SpiralAbyss(**data)

    async def get_notes(self, uid: int, *, lang: str = None) -> gmodels.Notes:
        """Get the real-time notes.

        :param uid: A Genshin uid
        :param lang: The language to use
        """
        server = utils.recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/dailyNote",
            lang=lang,
            params=dict(server=server, role_id=uid),
        )
        return gmodels.Notes(**data)

    async def get_activities(self, uid: int, *, lang: str = None) -> gmodels.Activities:
        """Get activities

        :param uid: A Genshin uid
        :param lang: The language to use
        """
        server = utils.recognize_server(uid)
        data = await self.request_game_record(
            "genshin/api/activities",
            lang=lang,
            params=dict(server=server, role_id=uid),
            cache=("activities", uid),
        )
        return gmodels.Activities(**data)

    async def get_full_user(self, uid: int, *, lang: str = None) -> gmodels.FullUserStats:
        """Get a user with all their possible data

        :param uid: A Genshin uid
        :param lang: The language to use
        """
        user, abyss1, abyss2, activities = await asyncio.gather(
            self.get_user(uid, lang=lang),
            self.get_spiral_abyss(uid, previous=False),
            self.get_spiral_abyss(uid, previous=True),
            self.get_activities(uid, lang=lang),
        )
        abyss = {"current": abyss1, "previous": abyss2}
        return gmodels.FullUserStats(**user.dict(), abyss=abyss, activities=activities)

    # LEDGER:

    async def get_diary(self, uid: int = None, *, month: int = None, lang: str = None) -> gmodels.Diary:
        """Get a traveler's diary with earning details for the month

        :param uid: Genshin uid of the currently logged-in user
        :param month: The month in the year to see the history for
        :param lang: The language to use
        """
        data = await self.request_ledger(uid, month=month, lang=lang)
        return gmodels.Diary(**data)

    def diary_log(
        self,
        uid: int = None,
        *,
        mora: bool = False,
        month: int = None,
        limit: int = None,
        lang: str = None,
    ) -> paginators.DiaryPaginator:
        """Create a new daily reward pagintor

        :param client: A client for making http requests
        :param uid: Genshin uid of the currently logged-in user
        :param mora: Whether the type of currency should be mora instead of primogems
        :param month: The month in the year to see the history for
        :param limit: The maximum amount of actions to get
        :param lang: The language to use
        """
        type = 2 if mora else 1
        return paginators.DiaryPaginator(self, uid, type, month, limit, lang)

    # CALCULATOR

    async def calculate(
        self,
        character: Union[Tuple[int, int, int], Tuple[int, int, int, int]] = None,
        weapon: Tuple[int, int, int] = None,
        artifacts: Union[Sequence[Tuple[int, int, int]], Mapping[int, Tuple[int, int]]] = None,
        talents: Union[Sequence[Tuple[int, int, int]], Mapping[int, Tuple[int, int]]] = None,
        *,
        lang: str = None,
    ):
        json: Dict[str, Any] = {}

        if character:
            if len(character) == 4:
                # highly problematic section for mypy, we have to be very explicit
                cid, json["element_attr_id"], cl, tl = cast(Tuple[int, int, int, int], character)
                character = (cid, cl, tl)

            json.update(gmodels.CalculatorObject(*character)._serialize(prefix="avatar_"))
            if character[0] in (10000005, 10000007):
                raise ValueError("No element provided for the traveler")

        if talents:
            if isinstance(talents, Mapping):
                talents = [(k, *v) for k, v in talents.items()]
            json["skill_list"] = [gmodels.CalculatorObject(*i)._serialize() for i in talents]

        if weapon:
            json["weapon"] = gmodels.CalculatorObject(*weapon)._serialize()

        if artifacts:
            if isinstance(artifacts, Mapping):
                artifacts = [(k, *v) for k, v in artifacts.items()]
            json["reliquary_list"] = [gmodels.CalculatorObject(*i)._serialize() for i in artifacts]

        data = await self.request_calculator("compute", lang=lang, json=json)
        return gmodels.CalculatorResult(**data)

    async def _get_calculator_items(
        self,
        slug: str,
        filters: Dict[str, Any],
        query: str = None,
        *,
        is_all: bool = False,
        sync: Union[int, bool] = False,
        lang: str = None,
    ) -> List[Dict[str, Any]]:
        """Get all items of a specific slug from a calculator"""
        if query and any(isinstance(v, list) and v for v in filters.values()):
            raise TypeError("Cannot specify a query and filter at the same time")

        endpoint = f"sync/{slug}/list" if sync else f"{slug}/list"
        json: Dict[str, Any] = dict(page=1, size=69420, is_all=is_all, **filters)
        if query:
            json.update(keywords=query)
        if sync:
            json.update(await self._complete_uid(sync if sync > 1 else None))

        data = await self.request_calculator(
            endpoint,
            lang=lang,
            json=json,
        )
        return data["list"]

    async def get_calculator_characters(
        self,
        *,
        query: str = None,
        elements: Sequence[int] = None,
        weapon_types: Sequence[int] = None,
        include_traveler: bool = False,
        sync: Union[int, bool] = False,
        lang: str = None,
    ) -> List[gmodels.CalculatorCharacter]:
        """Get all characters provided by the Enhancement Progression Calculator

        :param query: A query to use when searching; incompatible with other filters
        :param elements: The elements of returned characters - refer to `.models.CALCULATOR_ELEMENTS`
        :param weapon_types: The weapon types of returned characters - refer to `.models.CALCULATOR_WEAPON_TYPES`
        :param lang: The language to use
        """
        data = await self._get_calculator_items(
            "avatar",
            lang=lang,
            is_all=include_traveler,
            sync=sync,
            query=query,
            filters=dict(
                element_attr_ids=elements or [],
                weapon_cat_ids=weapon_types or [],
            ),
        )
        return [gmodels.CalculatorCharacter(**i) for i in data]

    async def get_calculator_weapons(
        self,
        *,
        query: str = None,
        types: Sequence[int] = None,
        rarities: Sequence[int] = None,
        lang: str = None,
    ) -> List[gmodels.CalculatorWeapon]:
        """Get all weapons provided by the Enhancement Progression Calculator

        :param query: A query to use when searching; incompatible with other filters
        :param types: The types of returned weapons - refer to `.models.CALCULATOR_WEAPON_TYPES`
        :param rarities: The rarities of returned weapons
        :param lang: The language to use
        """
        data = await self._get_calculator_items(
            "weapon",
            lang=lang,
            query=query,
            filters=dict(
                weapon_cat_ids=types or [],
                weapon_levels=rarities or [],
            ),
        )
        return [gmodels.CalculatorWeapon(**i) for i in data]

    async def get_calculator_artifacts(
        self,
        *,
        query: str = None,
        pos: int = 1,
        rarities: Sequence[int] = None,
        lang: str = None,
    ) -> List[gmodels.CalculatorArtifact]:
        """Get all artifacts provided by the Enhancement Progression Calculator

        :param query: A query to use when searching; incompatible with other filters
        :param pos: The slot position of the returned weapon
        :param rarities: The rarities of returned artifacts
        :param lang: The language to use
        """
        data = await self._get_calculator_items(
            "reliquary",
            lang=lang,
            query=query,
            filters=dict(
                reliquary_cat_id=pos,
                reliquary_levels=rarities or [],
            ),
        )
        return [gmodels.CalculatorArtifact(**i) for i in data]

    async def get_character_details(
        self,
        character_id: int,
        *,
        uid: int = None,
        lang: str = None,
    ) -> gmodels.CalculatorCharacterDetails:
        """Get the weapon, artifacts and talents of a character

        Not related to the Battle Chronicle. This data is always private.

        :param lang: The language to use
        """
        params = dict(avatar_id=character_id)
        params.update(await self._complete_uid(uid))

        data = await self.request_calculator(
            "sync/avatar/detail",
            method="GET",
            lang=lang,
            params=params,
        )
        return gmodels.CalculatorCharacterDetails(**data)

    async def get_character_talents(
        self,
        character_id: int,
        *,
        lang: str = None,
    ) -> List[gmodels.CalculatorTalent]:
        """Get the talents of a character

        This only gets the talent names, not their levels.
        Use `get_character_details` for precise information.

        :param lang: The language to use
        """
        data = await self.request_calculator(
            "avatar/skill_list",
            method="GET",
            lang=lang,
            params=dict(avatar_id=character_id),
        )
        return [gmodels.CalculatorTalent(**i) for i in data["list"]]

    async def get_complete_artifact_set(
        self,
        artifact_id: int,
        *,
        lang: str = None,
    ) -> List[gmodels.CalculatorArtifact]:
        """Get all other artifacts that share a set with any given artifact

        Doesn't return the artifact passed into this function.

        :param lang: The language to use
        """
        data = await self.request_calculator(
            "reliquary/set",
            method="GET",
            lang=lang,
            params=dict(reliquary_id=artifact_id),
        )
        return [gmodels.CalculatorArtifact(**i) for i in data["reliquary_list"]]

    # DAILY REWARDS:

    async def get_reward_info(self, *, lang: str = None) -> base_models.DailyRewardInfo:
        """Get the daily reward info for the current user

        :param lang: The language to use
        """
        data = await self.request_daily_reward("info", lang=lang)
        return base_models.DailyRewardInfo(data["is_sign"], data["total_sign_day"])

    async def get_monthly_rewards(self, *, lang: str = None) -> List[base_models.DailyReward]:
        """Get a list of all availible rewards for the current month

        :param lang: The language to use
        """
        func = utils.perm_cache(
            ("rewards", datetime.utcnow().month, lang or self.lang),
            self.request_daily_reward,
        )
        data = await func("home", lang=lang)
        return [base_models.DailyReward(**i) for i in data["awards"]]

    def claimed_rewards(self, *, limit: int = None, lang: str = None) -> paginators.DailyRewardPaginator:
        """Get all claimed rewards for the current user

        NOTE: Languages are currently broken,
        the language is based off the language used to claim the reward

        :param limit: The maximum amount of rewards to get
        :param lang: The language to use - currently broken
        """
        return paginators.DailyRewardPaginator(self, limit=limit, lang=lang)

    @overload
    async def claim_daily_reward(self, *, lang: str = None, reward: Literal[True] = ...) -> base_models.DailyReward:
        ...

    @overload
    async def claim_daily_reward(self, *, lang: str = None, reward: Literal[False]) -> None:
        ...

    async def claim_daily_reward(self, *, lang: str = None, reward: bool = True) -> Optional[base_models.DailyReward]:
        """Signs into hoyolab and claims the daily reward.

        :param lang: The language to use
        :param reward: Whether to also fetch the claimed reward
        """
        await self.request_daily_reward("sign", method="POST", lang=lang)

        if not reward:
            return None

        info, rewards = await asyncio.gather(
            self.get_reward_info(lang=lang),
            self.get_monthly_rewards(lang=lang),
        )
        return rewards[info.claimed_rewards - 1]

    # WISH HISTORY:

    @overload
    def wish_history(
        self,
        banner_type: Optional[List[gmodels.BannerType]] = ...,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> paginators.MergedWishHistory:
        ...

    @overload
    def wish_history(
        self,
        banner_type: gmodels.BannerType,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> paginators.WishHistory:
        ...

    def wish_history(
        self,
        banner_type: Union[gmodels.BannerType, List[gmodels.BannerType]] = None,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> Union[paginators.WishHistory, paginators.MergedWishHistory]:
        """Get the wish history of a user

        :param banner_type: The banner(s) from which to get the wishes
        :param limit: The maximum amount of wishes to get
        :param lang: The language to use
        :param authkey: The authkey to use when requesting data
        :param end_id: The ending id to start getting data from
        """
        cls = paginators.WishHistory if isinstance(banner_type, int) else paginators.MergedWishHistory
        return cls(
            self,
            banner_type,  # type: ignore
            lang=lang,
            authkey=authkey,
            limit=limit,
            end_id=end_id,
        )

    async def get_banner_names(self, *, lang: str = None, authkey: str = None) -> Dict[gmodels.BannerType, str]:
        """Get a list of banner names

        :param lang: The language to use
        :param authkey: The authkey to use when requesting data
        """
        func = perm_cache(("banners", lang or self.lang), self.request_gacha_info)
        data = await func(
            "getConfigList",
            lang=lang,
            authkey=authkey,
        )
        return {int(i["key"]): i["name"] for i in data["gacha_type_list"]}  # type: ignore

    async def _get_banner_details(self, banner_id: str, *, lang: str = None) -> gmodels.BannerDetails:
        """Get details of a specific banner using its id

        :param banner_id: A banner id
        :param lang: The language to use
        """
        data = await self.request_webstatic(f"/hk4e/gacha_info/os_asia/{banner_id}/{lang or self.lang}.json")
        return gmodels.BannerDetails(**data)

    async def get_banner_details(self, banner_ids: List[str] = None, *, lang: str = None) -> List[gmodels.BannerDetails]:
        """Get all banner details at once in a batch

        :param banner_ids: A list of banner ids, implicitly fetched when not provided
        :param lang: The language to use
        """
        try:
            banner_ids = banner_ids or utils.get_banner_ids()
        except FileNotFoundError:
            banner_ids = []

        if len(banner_ids) < 3:
            banner_ids = await self.fetch_banner_ids()

        data = await asyncio.gather(*(self._get_banner_details(i, lang=lang) for i in banner_ids))
        return list(data)

    async def get_gacha_items(self, *, server: str = "os_asia", lang: str = None) -> List[gmodels.GachaItem]:
        """Get the list of characters and weapons that can be gotten from the gacha.

        :param server: The server to request the items from
        :param lang: The language to use
        """
        data = await self.request_webstatic(f"/hk4e/gacha_info/{server}/items/{lang or self.lang}.json", cache=False)
        return [gmodels.GachaItem(**i) for i in data]

    # TRANSACTIONS:

    async def _get_transaction_reasons(self, lang: str) -> Dict[str, str]:
        """Get a mapping of transaction reasons

        :param lang: The language to use
        """
        base = "https://mi18n-os.mihoyo.com/webstatic/admin/mi18n/hk4e_global/"
        data = await self.request_webstatic(base + f"m02251421001311/m02251421001311-{lang}.json")

        return {k.split("_")[-1]: v for k, v in data.items() if k.startswith("selfinquiry_general_reason_")}

    @overload
    def transaction_log(
        self,
        kind: Optional[List[gmodels.TransactionKind]] = ...,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> paginators.MergedTransactions:
        ...

    @overload
    def transaction_log(
        self,
        kind: Literal["primogem", "crystal", "resin"],
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> paginators.Transactions[gmodels.Transaction]:
        ...

    @overload
    def transaction_log(
        self,
        kind: Literal["artifact", "weapon"],
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> paginators.Transactions[gmodels.ItemTransaction]:
        ...

    def transaction_log(
        self,
        kind: Union[gmodels.TransactionKind, List[gmodels.TransactionKind]] = None,
        *,
        limit: int = None,
        lang: str = None,
        authkey: str = None,
        end_id: int = 0,
    ) -> Union[paginators.Transactions[Any], paginators.MergedTransactions]:
        """Get the transaction log of a user

        :param kind: The kind(s) of transactions to get
        :param limit: The maximum amount of wishes to get
        :param lang: The language to use
        :param authkey: The authkey to use when requesting data
        :param end_id: The ending id to start getting data from
        """
        cls = paginators.Transactions if isinstance(kind, str) else paginators.MergedTransactions
        return cls(
            self,
            kind,  # type: ignore
            lang=lang,
            authkey=authkey,
            limit=limit,
            end_id=end_id,
        )

    @ensure_std_adapter
    async def _complete_uid(
        self,
        uid: Optional[int] = None,
        uid_key: str = "uid",
        server_key: str = "region",
    ) -> Dict[str, Any]:
        """Create a new dict with a uid and a server

        These are fetched from the currently authenticated user
        """
        params: Dict[str, Any] = {}

        uid = uid or self._uid

        if uid is None:
            accounts = await self.genshin_accounts()
            # filter test servers
            accounts = [account for account in accounts if "os" in account.server or "cn" in account.server]

            # TODO: Raise properly
            if not accounts:
                errors.raise_for_retcode({"retcode": -1073})

            account = max(accounts, key=lambda a: a.level)
            uid = account.uid

            self._uid = uid

        params[uid_key] = uid
        params[server_key] = utils.recognize_server(uid)

        return params

    async def _fetch_mi18n(self) -> Dict[str, Dict[str, str]]:
        if self.fetched_mi18n:
            return base_models.APIModel._mi18n

        self.fetched_mi18n = True

        async def single(url: str, key: str, lang: str = None):
            if lang is None:
                coros = (single(url, key, l) for l in LANGS)
                return await asyncio.gather(*coros)

            data = await self.request_webstatic(url.format(lang=lang))
            for k, v in data.items():
                base_models.APIModel._mi18n.setdefault(key + "/" + k, {})[lang] = v

        coros = (single(url, key) for key, url in base_models.APIModel._mi18n_urls.items())
        await asyncio.gather(*coros)

        return base_models.APIModel._mi18n

    async def init(self, lang: str = None):
        """Request all static & permanent endpoints to not require them later

        :param lang: The language to use
        """
        lang = lang or self.lang

        await asyncio.gather(
            self.get_banner_names(lang=lang),
            self.get_banner_details(lang=lang),
            self.get_monthly_rewards(),
            self._get_transaction_reasons(lang=lang),
            self._fetch_mi18n(),
        )

    async def fetch_banner_ids(self) -> List[str]:
        """Fetch banner ids from a user-mantained repo"""
        url = "https://raw.githubusercontent.com/thesadru/genshindata/master/banner_ids.txt"
        async with self.session.get(url) as r:
            data = await r.text()
        return data.splitlines()


class BaseOverseasGenshinClient(BaseGenshinClient, base.BaseAdapter):
    DS_SALT = "6cqshh5dhw73bzxn20oexa9k516chk7s"
    ACT_ID = "e202102251931481"

    WEBSTATIC_URL = "https://webstatic-sea.mihoyo.com/"
    TAKUMI_URL = "https://api-os-takumi.mihoyo.com/"
    RECORD_URL = "https://bbs-api-os.mihoyo.com/game_record/"
    INFO_LEDGER_URL = "https://hk4e-api-os.mihoyo.com/event/ysledgeros/month_info"
    DETAIL_LEDGER_URL = "https://hk4e-api-os.mihoyo.com/event/ysledgeros/month_detail"
    CALCULATOR_URL = "https://sg-public-api.mihoyo.com/event/calculateos/"
    REWARD_URL = "https://hk4e-api-os.mihoyo.com/event/sol/"
    GACHA_INFO_URL = "https://hk4e-api-os.mihoyo.com/event/gacha_info/api/"
    YSULOG_URL = "https://hk4e-api-os.mihoyo.com/ysulog/api/"
    MAP_URL = "https://api-os-takumi-static.mihoyo.com/common/map_user/ys_obc/v1/map/"
    STATIC_MAP_URL = "https://api-os-takumi-static.mihoyo.com/common/map_user/ys_obc/v1/map"


class BaseChineseGenshinClient(BaseGenshinClient, base.BaseAdapter):
    DS_SALT = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
    SIGNIN_SALT = "4a8knnbk5pbjqsrudp3dq484m9axoc5g"
    ACT_ID = "e202009291139501"

    TAKUMI_URL = "https://api-takumi.mihoyo.com/"
    RECORD_URL = "https://api-takumi.mihoyo.com/game_record/app/"
    INFO_LEDGER_URL = "https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo"
    DETAIL_LEDGER_URL = "https://hk4e-api.mihoyo.com/event/ys_ledger/monthDetail"
    REWARD_URL = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/"
    GACHA_INFO_URL = "https://hk4e-api.mihoyo.com/event/gacha_info/api/"
    MAP_URL = "https://api-takumi-static.mihoyo.com/common/map_user/ys_obc/v1/map/"
    STATIC_MAP_URL = "https://api-static.mihoyo.com/common/map_user/ys_obc/v1/map"
