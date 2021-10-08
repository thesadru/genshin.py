import pytest
from genshin import GenshinClient


@pytest.mark.asyncio
async def test_cache(client: GenshinClient, uid: int):
    # we only get the cookies from the old client
    cookies = client.cookies

    client = GenshinClient()
    client.set_cookies(cookies)
    client.cache = {}

    for _ in range(5):
        await client.get_user(uid)

    assert len(client.cache) == 2

    await client.get_gacha_items()

    assert client.static_cache and len(client.static_cache) == 1

    await client.close()
