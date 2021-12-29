from __future__ import annotations

import abc
import asyncio
from typing import *

from yarl import URL

from genshin import models as base_models
from genshin import paginators, utils
from genshin.client import adapter
from genshin.constants import LANGS

__all__ = ["APIClient", "ABCString", "ensure_std_adapter"]

CallableT = TypeVar("CallableT", bound=Callable[..., Any])
ABCString = cast(Type[str], NewType("ABCString", str))


def ensure_std_adapter(func: CallableT) -> CallableT:
    def wrapper(self: adapter.Adapter, *args: Any, **kwargs: Any) -> Any:
        if isinstance(self, adapter.MultiCookieAdapter):
            raise AttributeError(f"'{type(self)}' object has no method '{func.__name__}'")

        return func(self, *args, **kwargs)

    return functools.update_wrapper(wrapper, func)  # type: ignore


class APIClient(adapter.BaseAdapter):
    """A mixin api client which allows requests for shared endpoints"""

    DS_SALT: ABCString
    ACT_ID: ABCString

    TAKUMI_URL: ABCString
    RECORD_URL: ABCString
    REWARD_URL: ABCString

    if not TYPE_CHECKING:

        def __new__(cls):
            """Create a new instance and check for the presence of ABCString"""
            attribs: List[str] = []

            type_hints = get_type_hints(cls)
            for name, annotation in type_hints.items():
                if annotation is ABCString and not hasattr(cls, name):
                    attribs.append(name)

            if attribs:
                raise TypeError(
                    f"Can't instantiate abstract class {cls.__name__} with abstract attributes " + ", ".join(attribs)
                )

            return super().__new__(cls)

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
        **kwargs: Any,
    ):
        """Make a request towards the game record endpoint

        User stats related data
        """
        # this is simply just an alias for shorter request endpoints
        url = URL(self.RECORD_URL).join(URL(endpoint))

        return await self.request_hoyolab(url, method=method, **kwargs)

    # TODO: Daily rewards for standard adapters

    async def _fetch_mi18n(self) -> Dict[str, Dict[str, str]]:
        if self.fetched_mi18n:
            return base_models.APIModel._mi18n

        self.fetched_mi18n = True

        async def single(url: str, key: str, lang: str = None) -> Any:
            if lang is None:
                coros = (single(url, key, l) for l in LANGS)
                return await asyncio.gather(*coros)

            data = await self.request_webstatic(url.format(lang=lang))
            for k, v in data.items():
                base_models.APIModel._mi18n.setdefault(key + "/" + k, {})[lang] = v

            return data

        coros = (single(url, key) for key, url in base_models.APIModel._mi18n_urls.items())
        await asyncio.gather(*coros)

        return base_models.APIModel._mi18n
