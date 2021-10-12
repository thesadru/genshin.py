import asyncio
import time

import cachetools
import pytest
from genshin import GenshinClient


@pytest.mark.asyncio_cooperative
async def test_cache(client: GenshinClient, uid: int):
    # we only get the cookies from the old client
    cookies = client.cookies

    client = GenshinClient()
    client.set_cookies(cookies)

    client.cache = {}

    for _ in range(5):
        await client.get_partial_user(uid)

    assert len(client.cache) == 1

    await client.close()


@pytest.mark.asyncio_cooperative
async def test_static_cache(client: GenshinClient):
    cookies = client.cookies

    client = GenshinClient()
    client.set_cookies(cookies)

    # hack to clear the cache while making concurrency possible
    client.static_cache = {}  # type: ignore

    await client.get_gacha_items()

    assert len(client.static_cache) == 1

    await client.close()


@pytest.mark.asyncio_cooperative
async def test_cachetools_cache(client: GenshinClient, uid: int):
    cookies = client.cookies

    client = GenshinClient()
    client.set_cookies(cookies)
    client.set_cache(1024, ttl=1)
    assert isinstance(client.cache, cachetools.TTLCache) and client.cache.ttl == 1

    await client.get_partial_user(uid)

    await asyncio.sleep(1.1)

    assert len(client.cache) == 0

    await client.close()
