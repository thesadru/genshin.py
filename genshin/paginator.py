"""Paginators for abstracting paginated resources"""
from __future__ import annotations

import abc
import asyncio
import heapq
from datetime import datetime
from typing import *

from .models import *
from .utils import aislice, amerge

if TYPE_CHECKING:
    from .client import ChineseClient, GenshinClient

__all__ = [
    "BasePaginator",
    "DailyRewardPaginator",
    "ChineseDailyRewardPaginator",
    "DiaryPaginator",
    "IDPagintor",
    "AuthkeyPaginator",
    "WishHistory",
    "Transactions",
    "MergedPaginator",
    "MergedWishHistory",
    "MergedTransactions",
]


class _Model(Protocol):
    id: int
    time: datetime


T = TypeVar("T", bound=Any)
MT = TypeVar("MT", bound=_Model, covariant=True)
TransactionT = TypeVar("TransactionT", bound=BaseTransaction, covariant=True)


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


class DiaryPaginator(BasePaginator):
    """A paginator specifically for diary entries"""

    # TODO: Option to merge all months together
    client: GenshinClient

    uid: Optional[int]
    type: int
    month: Optional[int]
    limit: Optional[int]
    lang: Optional[str]

    _data: Optional[BaseDiary] = None
    page_size: int = 10

    def __init__(
        self,
        client: GenshinClient,
        uid: int = None,
        type: int = 1,
        month: int = None,
        limit: int = None,
        lang: str = None,
    ) -> None:
        """Create a new daily reward pagintor

        :param client: A client for making http requests
        :param uid: Genshin uid of the currently logged-in user
        :param type: The type of currency to get
        :param month: The month in the year to see the history for
        :param limit: The maximum amount of actions to get
        :param lang: The language to use
        """
        self.client = client
        self.uid = uid
        self.type = type
        self.month = month
        self.limit = limit
        self.lang = lang

        self.current_page = 1

    @property
    def exhausted(self) -> bool:
        """Whether all pages have been fetched"""
        return self.current_page is None

    def __repr__(self) -> str:
        return f"{type(self).__name__}(uid={self.uid}, type={self.type}, limit={self.limit})"

    async def _get_page(self, page: int) -> DiaryPage:
        data = await self.client.request_ledger(
            self.uid,
            detail=True,
            month=self.month,
            lang=self.lang,
            params=dict(type=self.type, current_page=page, limit=10),
        )
        return DiaryPage(**data)

    async def next_page(self) -> List[DiaryAction]:
        """Get the next page of the paginator"""
        if self.current_page is None:
            raise Exception("No more pages")

        page = await self._get_page(self.current_page)
        self._data = page

        actions = page.actions

        if len(actions) < self.page_size:
            self.current_page = None
            return actions

        self.current_page += 1
        return actions

    async def _iter(self) -> AsyncIterator[DiaryAction]:
        """Iterate over pages until the end"""
        while not self.exhausted:
            page = await self.next_page()
            for i in page:
                yield i

    def __aiter__(self) -> AsyncIterator[DiaryAction]:
        """Iterate over all pages until the limit is reached"""
        return aislice(self._iter(), self.limit)

    @property
    def data(self) -> BaseDiary:
        """Get data bound to the diary

        This requires at least one page to have been fetched
        """
        if self._data is None:
            raise RuntimeError("At least one item must be fetched before data can be gotten")

        return self._data


class IDPagintor(BasePaginator, Generic[MT]):
    """A paginator of genshin end_id pages"""

    __repr_args__: Sequence[str] = ["limit"]

    client: GenshinClient
    limit: Optional[int]
    end_id: Optional[int]

    page_size: int = 20

    def __init__(self, client: GenshinClient, *, limit: int = None, end_id: int = 0) -> None:
        """Create a new paginator

        :param client: A client for making http requests
        :param limit: The maximum amount of rewards to get
        :param end_id: The ending id to start getting data from
        """
        self.client = client
        self.limit = limit
        self.end_id = end_id

    @property
    def exhausted(self) -> bool:
        """Whether all pages have been fetched"""
        return self.end_id is None

    def __repr__(self) -> str:
        args = ", ".join(f"{i}={getattr(self, i)!r}" for i in self.__repr_args__)
        return f"{type(self).__name__}({args})"

    async def _get_page(self, end_id: int) -> List[MT]:
        raise NotImplementedError

    def _cache_key(self, end_id: int) -> Tuple[int, str]:
        return (end_id, "")

    def _update_cache(self, data: List[MT]) -> bool:
        if self.client.paginator_cache is None:
            return False

        cache = self.client.paginator_cache

        if self.end_id:
            cache[self._cache_key(self.end_id)] = data[0]

        for p, n in zip(data, data[1:]):
            cache[self._cache_key(p.id)] = n

        return True

    def _collect_cache(self) -> Iterator[MT]:
        cache = self.client.paginator_cache
        if cache is None or self.end_id is None:
            return

        key = self._cache_key(self.end_id)
        while key in cache:
            yield cache[key]
            self.end_id = cache[key].id
            key = self._cache_key(self.end_id)

    async def next_page(self) -> List[MT]:
        """Get the next page of the paginator"""
        if self.end_id is None:
            raise Exception("No more pages")

        data = await self._get_page(self.end_id)

        self._update_cache(data)

        # mark paginator as exhausted
        if len(data) < self.page_size:
            self.end_id = None
            return data

        self.end_id = data[-1].id
        return data

    async def _iter(self) -> AsyncIterator[MT]:
        """Iterate over pages until the end"""
        # tfw no yield from in asyn iterators
        while self.end_id is not None:
            for i in self._collect_cache():
                yield i

            page = await self.next_page()
            for i in page:
                yield i

    def __aiter__(self) -> AsyncIterator[MT]:
        """Iterate over all pages until the limit is reached"""
        return aislice(self._iter(), self.limit)

    async def flatten(self, *, lazy: bool = True) -> List[MT]:
        """Flatten the entire iterator into a list

        :param lazy: Limit to only one request at a time
        """
        return [item async for item in self]

    async def first(self) -> MT:
        """Get the very first item"""
        x = await self._iter().__anext__()
        self.end_id = None  # invalidate the iterator
        return x


class AuthkeyPaginator(IDPagintor[MT]):
    """A paginator which utilizes authkeys"""

    __repr_args__ = ["limit", "lang"]

    _authkey: Optional[str]
    _lang: Optional[str]

    def __init__(
        self,
        client: GenshinClient,
        lang: str = None,
        authkey: str = None,
        limit: int = None,
        end_id: int = 0,
    ) -> None:
        """Create a new authkey paginator

        :param client: A client for making http requests
        :param lang: The language to use
        :param authkey: The authkey to use when requesting data
        :param limit: The maximum amount of rewards to get
        :param end_id: The ending id to start getting data from
        """
        super().__init__(client, limit=limit, end_id=end_id)
        self._lang = lang
        self._authkey = authkey

    @property
    def lang(self) -> str:
        """The language used for fetching data"""
        return self._lang or self.client.lang

    @property
    def authkey(self) -> str:
        """The authkey used for fetching data"""
        authkey = self._authkey or self.client.authkey
        if authkey is None:
            raise RuntimeError("No authkey set for client")

        return authkey


class WishHistory(AuthkeyPaginator[Wish]):
    """A paginator for wishes"""

    __repr_args__ = ["banner_type", "limit", "lang"]

    client: GenshinClient
    banner_type: BannerType

    def __init__(self, client: GenshinClient, banner_type: BannerType, **kwargs: Any) -> None:
        """Create a new wish history paginator

        :param client: A client for making http requests
        :param banner_type: The banner from which to get the wishes
        :param lang: The language to use
        :param authkey: The authkey to use when requesting data
        :param limit: The maximum amount of rewards to get
        :param end_id: The ending id to start getting data from
        """
        super().__init__(client, **kwargs)
        if banner_type not in [100, 200, 301, 302]:
            raise ValueError(f"Invalid banner type: {banner_type!r}")
        self.banner_type = banner_type

    def _cache_key(self, end_id: int) -> Tuple[int, str]:
        return (end_id, self.lang)

    async def _get_banner_name(self) -> str:
        """Get the banner name of banner_type"""
        banner_types = await self.client.get_banner_names(lang=self._lang, authkey=self._authkey)
        return banner_types[self.banner_type]

    async def _get_page(self, end_id: int) -> List[Wish]:
        data = await self.client.request_gacha_info(
            "getGachaLog",
            lang=self._lang,
            authkey=self._authkey,
            params=dict(gacha_type=self.banner_type, size=self.page_size, end_id=end_id),
        )
        banner_name = await self._get_banner_name()
        return [Wish(**i, banner_name=banner_name) for i in data["list"]]


class Transactions(AuthkeyPaginator[TransactionT]):
    """A paginator for transactions"""

    __repr_args__ = ["kind", "limit", "lang"]

    client: GenshinClient
    kind: TransactionKind

    def __init__(self, client: GenshinClient, kind: TransactionKind, **kwargs: Any) -> None:
        """Create a new transaction paginator

        :param client: A client for making http requests
        :param kind: The kind of transactions to get
        :param lang: The language to use
        :param authkey: The authkey to use when requesting data
        :param limit: The maximum amount of rewards to get
        :param end_id: The ending id to start getting data from
        """
        super().__init__(client, **kwargs)
        if kind not in ["primogem", "crystal", "resin", "artifact", "weapon"]:
            raise ValueError(f"Invalid transaction kind: {kind}")
        self.kind = kind

    def _cache_key(self, end_id: int) -> Tuple[int, str]:
        return (end_id, self.lang)

    async def _get_page(self, end_id: int):
        endpoint = "get" + self.kind.capitalize() + "Log"

        data, reasons = await asyncio.gather(
            self.client.request_transaction(
                endpoint,
                lang=self._lang,
                authkey=self._authkey,
                params=dict(end_id=end_id, size=20),
            ),
            self.client._get_transaction_reasons(self.lang),
        )

        transactions = []
        for trans in data["list"]:
            cls = ItemTransaction if "name" in trans else Transaction
            reason_id = trans["reason"]
            trans = {**trans, "reason_id": reason_id, "reason": reasons.get(reason_id, "")}
            transactions.append(cls(**trans, kind=self.kind))

        return transactions


class MergedPaginator(AuthkeyPaginator[MT]):
    """A paginator merging a collection of other paginators"""

    _paginators: List[IDPagintor[MT]]

    def __init__(self, client: GenshinClient, **kwargs: Any) -> None:
        super().__init__(client, **kwargs)

    def next_page(self) -> NoReturn:
        raise RuntimeError('Merged paginators cannot be gotten by "pages"')

    def _key(self, item: _Model) -> float:
        return item.time.timestamp()

    def _iter(self) -> AsyncIterator[MT]:
        return amerge(self._paginators, key=self._key)

    async def flatten(self, *, lazy: bool = False) -> List[MT]:
        if self.limit is not None and lazy:
            it = aislice(amerge(self._paginators, key=self._key), self.limit)
            return [x async for x in it]

        coros = (p.flatten() for p in self._paginators)
        lists = await asyncio.gather(*coros)
        return list(heapq.merge(*lists, key=self._key))[: self.limit]


class MergedWishHistory(MergedPaginator[Wish]):
    """A paginator for wish histories from multiple banners"""

    __repr_args__ = ["banner_types", "limit", "lang"]

    client: GenshinClient
    banner_types: List[BannerType]

    def __init__(
        self,
        client: GenshinClient,
        banner_types: List[BannerType] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new merged wish history paginator

        :param client: A client for making http requests
        :param banner_types: The banners from which to get the wishes
        :param lang: The language to use
        :param authkey: The authkey to use when requesting data
        :param limit: The maximum amount of rewards to get
        :param end_id: The ending id to start getting data from
        """
        super().__init__(client, **kwargs)
        self.banner_types = banner_types or [100, 200, 301, 302]

        self._paginators = [WishHistory(client, b, **kwargs) for b in self.banner_types]

    async def flatten(self, *, lazy: bool = False) -> List[Wish]:
        # before we gather all histories we should get the banner name
        asyncio.create_task(self.client.get_banner_names(lang=self._lang, authkey=self._authkey))
        return await super().flatten(lazy=lazy)


class MergedTransactions(MergedPaginator[BaseTransaction]):
    """A paginator for transactions from multiple banners"""

    __repr_args__ = ["kinds", "limit", "lang"]

    client: GenshinClient
    kinds: List[TransactionKind]

    def __init__(
        self,
        client: GenshinClient,
        kinds: List[TransactionKind] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new transaction paginator

        :param client: A client for making http requests
        :param kinds: The kinds of transactions to get
        :param lang: The language to use
        :param authkey: The authkey to use when requesting data
        :param limit: The maximum amount of rewards to get
        :param end_id: The ending id to start getting data from
        """
        super().__init__(client, **kwargs)
        self.kinds = kinds or ["primogem", "crystal", "resin", "artifact", "weapon"]

        self._paginators = [Transactions(client, kind, **kwargs) for kind in self.kinds]
