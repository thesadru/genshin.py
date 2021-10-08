import pytest

from genshin import GenshinClient


@pytest.mark.asyncio
async def test_record_card(client: GenshinClient, hoyolab_uid: int):
    data = await client.get_record_card(hoyolab_uid)

    pretty = data.as_dict()
    assert pretty["Days Active"] == data.days_active


@pytest.mark.asyncio
async def test_user(client: GenshinClient, uid: int):
    data = await client.get_user(uid)

    pretty = data.stats.as_dict()
    assert "Anemoculi" in pretty


@pytest.mark.asyncio
async def test_abyss(client: GenshinClient, uid: int):
    data = await client.get_spiral_abyss(uid, previous=True)

    pretty = data.ranks.as_dict()
    assert "Most Kills" in pretty


@pytest.mark.asyncio
async def test_exception(client: GenshinClient):
    with pytest.raises(Exception):
        await client.get_record_card(10000000)
