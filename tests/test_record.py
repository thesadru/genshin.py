import asyncio
from datetime import datetime

import pytest

import genshin
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
    assert data.characters[0].weapon


@pytest.mark.asyncio
async def test_partial_user(client: GenshinClient, uid: int):
    data = await client.get_partial_user(uid)
    assert not hasattr(data.characters[0], "weapon")


@pytest.mark.asyncio
async def test_abyss(client: GenshinClient, uid: int):
    data = await client.get_spiral_abyss(uid, previous=True)

    pretty = data.ranks.as_dict("zh-cn")
    assert "最多击破数" in pretty


@pytest.mark.asyncio
async def test_notes(lclient: GenshinClient, uid: int):
    pytest.skip("Notes depend on the player having their comissions completed")

    data = await lclient.get_notes(uid)

    assert data.resin_recovered_at >= datetime.now().astimezone()
    assert data.max_comissions == 4
    assert not (data.completed_commissions != 4 and data.claimed_comission_reward)
    assert len(data.expeditions) == 5


@pytest.mark.asyncio
async def test_activities(client: GenshinClient, uid: int):
    data = await client.get_activities(uid)

    assert data.hyakunin_ikki is not None
    assert data.hyakunin_ikki.challenges[0].medal == "gold"

    # mihoyo removed these???
    # assert data.labyrinth_warriors is not None
    # assert data.labyrinth_warriors.challenges[0].runes[0].element == "Anemo"


@pytest.mark.asyncio
async def test_full_user(client: GenshinClient, uid: int):
    data = await client.get_full_user(uid)
    assert data.abyss.previous is not None


@pytest.mark.asyncio
async def test_exceptions(client: GenshinClient):
    with pytest.raises(genshin.DataNotPublic):
        await client.get_record_card(10000000)

    with pytest.raises(genshin.AccountNotFound):
        await client.get_user(70000001)
