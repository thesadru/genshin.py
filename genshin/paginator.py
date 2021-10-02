from __future__ import annotations

from typing import *
from .models import Wish

if TYPE_CHECKING:
    from .client import GenshinClient


class IDModel(Protocol):
    id: int


IDModelT = TypeVar("IDModelT", bound=IDModel, covariant=True)
T = TypeVar("T")


async def aenumerate(aiterable: AsyncIterable[T], start: int = 0) -> AsyncIterator[Tuple[int, T]]:
    i = start
    async for x in aiterable:
        yield i, x
        i += 1


class IDPagintor(Generic[IDModelT]):
    """A paginator of genshin prev_id pages

    Takes in a function with which to get the next few arguments
    """

    limit: Optional[int]
    end_id: Optional[int]
    
    page_size: int = 20

    def __init__(self, limit: int = None, end_id: int = 0) -> None:
        """Create a new paginator from alimit and the starting end id"""
        self.limit = limit
        self.end_id = end_id
    
    @property
    def completed(self) -> bool:
        return self.end_id is None

    async def function(self, end_id: int) -> List[IDModelT]:
        raise NotImplementedError

    async def next_page(self) -> List[IDModelT]:
        """Get the next page of the paginator"""
        if self.end_id is None:
            raise Exception("No more pages")
        
        data = await self.function(self.end_id)
        
        # mark paginator as exhausted
        if len(data) < self.page_size:
            self.end_id = None
            return data
        
        self.end_id = data[-1].id
        return data
        

    async def _iter(self) -> AsyncIterator[IDModelT]:
        """Iterate over pages until the end"""
        while not self.completed:
            page = await self.next_page()
            for i in page:
                yield i

    async def __aiter__(self) -> AsyncIterator[IDModelT]:
        """Iterate over all pages unril the limit is reached"""
        async for i, x in aenumerate(self._iter(), start=1):
            yield x

            if self.limit and i >= self.limit:
                return


class AuthkeyPaginator(IDPagintor[IDModelT]):
    authkey: Optional[str]

    def __init__(self, authkey: str = None, limit: int = None, end_id: int = 0) -> None:
        super().__init__(limit=limit, end_id=end_id)
        self.authkey = authkey


class WishHistory(AuthkeyPaginator[Wish]):
    def __init__(self, client: GenshinClient, banner_type: int, lang: str = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client
        self.banner_type = banner_type
        self.lang = lang

    async def function(self, end_id: int) -> List[Wish]:
        data = await self.client.request_gacha_info(
            "getGachaLog", 
            lang=self.lang, 
            authkey=self.authkey, 
            params=dict(gacha_type=self.banner_type, size=self.page_size, end_id=end_id)
        )
        return [Wish(**i) for i in data["list"]]
        