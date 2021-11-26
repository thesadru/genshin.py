import asyncio

import pytest

import genshin
from genshin import ChineseClient


@pytest.mark.asyncio
async def test_record_card(cnclient: ChineseClient, miyoushe_uid: int):
    pytest.skip("Miyoushe uid points to a private record")

    data = await cnclient.get_record_card(miyoushe_uid)

    pretty = data.as_dict()
    assert pretty["Days Active"] == data.days_active


@pytest.mark.asyncio
async def test_user(cnclient: ChineseClient, cnuid: int):
    data = await cnclient.get_user(cnuid)

    pretty = data.stats.as_dict()
    assert "Anemoculi" in pretty
    assert data.characters[0].weapon


@pytest.mark.asyncio
async def test_partial_user(cnclient: ChineseClient, cnuid: int):
    data = await cnclient.get_partial_user(cnuid)
    assert not hasattr(data.characters[0], "weapon")


@pytest.mark.asyncio
async def test_characters(cnclient: ChineseClient, cnuid: int):
    user, partial = await asyncio.gather(cnclient.get_user(cnuid), cnclient.get_partial_user(cnuid))

    characters = await cnclient.get_characters(cnuid, [c.id for c in partial.characters])
    assert characters == user.characters


@pytest.mark.asyncio
async def test_abyss(cnclient: ChineseClient, cnuid: int):
    data = await cnclient.get_spiral_abyss(cnuid, previous=True)

    pretty = data.ranks.as_dict()
    assert "Most Defeats" in pretty


@pytest.mark.asyncio
async def test_activities(cnclient: ChineseClient, cnuid: int):
    data = await cnclient.get_activities(cnuid)

    assert data.chess is None


@pytest.mark.asyncio
async def test_full_user(cnclient: ChineseClient, cnuid: int):
    data = await cnclient.get_full_user(cnuid)
    assert data.abyss.previous is not None


@pytest.mark.asyncio
async def test_exceptions(cnclient: ChineseClient):
    with pytest.raises(genshin.DataNotPublic):
        await cnclient.get_record_card(10000000)

    with pytest.raises(genshin.AccountNotFound):
        await cnclient.get_user(70000001)


@pytest.mark.asyncio
async def test_diary(lcnclient: ChineseClient):
    diary = await lcnclient.get_diary()


@pytest.mark.asyncio
async def test_diary_log(lcnclient: ChineseClient):
    log = lcnclient.diary_log(limit=10)
    data = await log.flatten()

    assert log.data.uid == lcnclient.uid
    if data:
        assert data[0].amount > 0
