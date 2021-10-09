import pytest
import asyncio

from genshin import GenshinClient


@pytest.mark.asyncio_cooperative
async def test_search(client: GenshinClient, hoyolab_uid: int):
    users = await client.search_users("sadru")

    for user in users:
        if user.hoyolab_uid == hoyolab_uid:
            break
    else:
        raise AssertionError("Search did not return the correct users")

    assert user.nickname == "sadru"


@pytest.mark.asyncio_cooperative
async def test_recommended_users(client: GenshinClient):
    users = await client.get_recommended_users()

    assert len(users) > 80


@pytest.mark.asyncio_cooperative
async def test_genshin_accounts(lclient: GenshinClient, uid: int):
    accounts = await lclient.genshin_accounts()
    assert uid in [account.uid for account in accounts]


@pytest.mark.asyncio_cooperative
async def test_redeem_code(lclient: GenshinClient):

    with pytest.raises(Exception):
        await lclient.redeem_code("genshingift")

    await asyncio.sleep(5)  # ratelimit

    with pytest.raises(Exception):
        await lclient.redeem_code("invalid")
