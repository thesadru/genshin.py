import pytest
from genshin import GenshinClient


@pytest.mark.asyncio
async def test_wish_history(lclient: GenshinClient):
    history = await lclient.wish_history(200, limit=20).flatten()
    assert history[0].banner_type == 200
    assert history[0].banner_name == "Permanent Wish"


@pytest.mark.asyncio
async def test_merged_wish_history(lclient: GenshinClient):
    async for wish in lclient.wish_history(limit=30):
        assert wish


@pytest.mark.asyncio
async def test_filtered_merged_wish_history(lclient: GenshinClient):
    async for wish in lclient.wish_history([301, 302], limit=20):
        assert wish.banner_type in [301, 302]


@pytest.mark.asyncio
async def test_banner_types(lclient: GenshinClient):
    banner_types = await lclient.get_banner_names()
    assert sorted(banner_types.keys()) == [100, 200, 301, 302]


@pytest.mark.asyncio
async def test_banner_details(lclient: GenshinClient):
    banners = await lclient.get_banner_details()
    for details in banners:
        assert details.banner_type in [100, 200, 301, 302]


@pytest.mark.asyncio
async def test_gacha_items(lclient: GenshinClient):
    items = await lclient.get_gacha_items()
    assert items[0].is_character()
    assert not items[-1].is_character()
