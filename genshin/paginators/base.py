from __future__ import annotations

import abc
from typing import *

from ..models import *
from ..utils import aislice

if TYPE_CHECKING:
    from ..client import ChineseClient, GenshinClient

__all__ = (
    "BasePaginator",
    "DailyRewardPaginator",
    "ChineseDailyRewardPaginator",
)


class BasePaginator(abc.ABC):
    """A base paginator requiring the implementation of some methods"""

    @property
    @abc.abstractmethod
    def exhausted(self) -> bool:
        ...

    @abc.abstractmethod
    async def next_page(self) -> Any:
        ...

    @abc.abstractmethod
    def __aiter__(self) -> AsyncIterator[Any]:
        ...

    async def flatten(self) -> Sequence[Any]:
        return [item async for item in self]

    def __await__(self) -> Generator[Any, Any, Sequence[Any]]:
        return self.flatten().__await__()


class DailyRewardPaginator(BasePaginator):
    """A paginator specifically for claimed daily rewards"""

    client: GenshinClient
    limit: Optional[int]
    lang: Optional[str]
    current_page: Optional[int]

    page_size: int = 10

    def __init__(self, client: GenshinClient, limit: int = None, lang: str = None) -> None:
        """Create a new daily reward pagintor

        :param client: A client for making http requests
        :param limit: The maximum amount of rewards to get
        :param lang: The language to use - currently broken
        """
        self.client = client
        self.limit = limit
        self.lang = lang

        self.current_page = 1

    @property
    def exhausted(self) -> bool:
        """Whether all pages have been fetched"""
        return self.current_page is None

    def __repr__(self) -> str:
        return f"{type(self).__name__}(limit={self.limit})"

    async def _get_page(self, page: int) -> List[ClaimedDailyReward]:
        params = dict(current_page=page)
        data = await self.client.request_daily_reward("award", params=params, lang=self.lang)
        return [ClaimedDailyReward(**i) for i in data["list"]]

    async def next_page(self) -> List[ClaimedDailyReward]:
        """Get the next page of the paginator"""
        if self.current_page is None:
            raise Exception("No more pages")

        data = await self._get_page(self.current_page)

        if len(data) < self.page_size:
            self.current_page = None
            return data

        self.current_page += 1
        return data

    async def _iter(self) -> AsyncIterator[ClaimedDailyReward]:
        """Iterate over pages until the end"""
        while not self.exhausted:
            page = await self.next_page()
            for i in page:
                yield i

    def __aiter__(self) -> AsyncIterator[ClaimedDailyReward]:
        """Iterate over all pages until the limit is reached"""
        return aislice(self._iter(), self.limit)


class ChineseDailyRewardPaginator(DailyRewardPaginator):
    """A paginator specifically for claimed daily rewards on chinese bbs"""

    client: ChineseClient
    uid: Optional[int]
    limit: Optional[int]
    current_page: Optional[int]

    page_size: int = 10

    def __init__(self, client: ChineseClient, uid: int = None, limit: int = None) -> None:
        """Create a new daily reward pagintor

        :param client: A client for making http requests
        :param uid: Genshin uid of the currently logged-in user
        :param limit: The maximum amount of rewards to get
        """
        self.client = client
        self.uid = uid
        self.limit = limit

    async def _get_page(self, page: int) -> List[ClaimedDailyReward]:
        params = dict(current_page=page)
        data = await self.client.request_daily_reward("award", self.uid, params=params)
        return [ClaimedDailyReward(**i) for i in data["list"]]