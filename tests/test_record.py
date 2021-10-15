import asyncio

import genshin
import pytest
from genshin import GenshinClient


@pytest.mark.asyncio_cooperative
async def test_record_card(client: GenshinClient, hoyolab_uid: int):
    data = await client.get_record_card(hoyolab_uid)

    pretty = data.as_dict()
    assert pretty["Days Active"] == data.days_active


@pytest.mark.asyncio_cooperative
async def test_user(client: GenshinClient, uid: int):
    data = await client.get_user(uid)

    pretty = data.stats.as_dict()
    assert "Anemoculi" in pretty
    assert data.characters[0].weapon


@pytest.mark.asyncio_cooperative
async def test_partial_user(client: GenshinClient, uid: int):
    data = await client.get_partial_user(uid)
    assert not hasattr(data.characters[0], "weapon")


@pytest.mark.asyncio_cooperative
async def test_characters(client: GenshinClient, uid: int):
    user, partial = await asyncio.gather(client.get_user(uid), client.get_partial_user(uid))

    characters = await client.get_characters(uid, [c.id for c in partial.characters])
    assert characters == user.characters


@pytest.mark.asyncio_cooperative
async def test_abyss(client: GenshinClient, uid: int):
    data = await client.get_spiral_abyss(uid, previous=True)

    pretty = data.ranks.as_dict()
    assert "Most Kills" in pretty


@pytest.mark.asyncio_cooperative
async def test_activities(client: GenshinClient, uid: int):
    data = await client.get_activities(uid)

    assert data.hyakunin.challenges[0].medal == "gold"


@pytest.mark.asyncio_cooperative
async def test_full_user(client: GenshinClient, uid: int):
    data = await client.get_full_user(uid)


@pytest.mark.asyncio_cooperative
async def test_exceptions(client: GenshinClient):
    with pytest.raises(genshin.DataNotPublic):
        await client.get_record_card(10000000)

    with pytest.raises(genshin.AccountNotFound):
        await client.get_user(70000001)
