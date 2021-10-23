import asyncio

import genshin
import pytest
from genshin import ChineseClient


@pytest.mark.asyncio_cooperative
async def test_user(cnclient: ChineseClient, cnuid: int):
    data = await cnclient.get_user(cnuid)

    pretty = data.stats.as_dict()
    assert "Anemoculi" in pretty
    assert data.characters[0].weapon


@pytest.mark.asyncio_cooperative
async def test_partial_user(cnclient: ChineseClient, cnuid: int):
    data = await cnclient.get_partial_user(cnuid)
    assert not hasattr(data.characters[0], "weapon")


@pytest.mark.asyncio_cooperative
async def test_characters(cnclient: ChineseClient, cnuid: int):
    user, partial = await asyncio.gather(cnclient.get_user(cnuid), cnclient.get_partial_user(cnuid))

    characters = await cnclient.get_characters(cnuid, [c.id for c in partial.characters])
    assert characters == user.characters


@pytest.mark.asyncio_cooperative
async def test_abyss(cnclient: ChineseClient, cnuid: int):
    data = await cnclient.get_spiral_abyss(cnuid, previous=True)

    pretty = data.ranks.as_dict()
    assert "Most Kills" in pretty


@pytest.mark.asyncio_cooperative
async def test_activities(cnclient: ChineseClient, cnuid: int):
    data = await cnclient.get_activities(cnuid)

    assert data.chess is None


@pytest.mark.asyncio_cooperative
async def test_full_user(cnclient: ChineseClient, cnuid: int):
    data = await cnclient.get_full_user(cnuid)
    assert data.abyss.previous is not None


@pytest.mark.asyncio_cooperative
async def test_exceptions(cnclient: ChineseClient):
    with pytest.raises(genshin.DataNotPublic):
        await cnclient.get_record_card(10000000)

    with pytest.raises(genshin.AccountNotFound):
        await cnclient.get_user(70000001)
