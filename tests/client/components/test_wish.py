import pytest

import genshin


async def test_wish_history(lclient: genshin.Client, authkey: str):
    history = await lclient.wish_history(200, limit=20).flatten()

    assert history[0].banner_type == 200
    assert history[0].banner_name == "Permanent Wish"


async def test_merged_wish_history(lclient: genshin.Client, authkey: str):
    async for wish in lclient.wish_history([200, 302], limit=20):
        assert wish.banner_type in [200, 302]


async def test_banner_types(lclient: genshin.Client, authkey: str):
    banner_types = await lclient.get_banner_names()
    assert sorted(banner_types.keys()) == [100, 200, 301, 302]


async def test_banner_details(lclient: genshin.Client):
    try:
        banners = await lclient.get_banner_details()
    except FileNotFoundError:
        # running in a vm
        pytest.skip("No genshin installation.")

    for details in banners:
        assert details.banner_type in [100, 200, 301, 302, 400, 500]


# async def test_gacha_items(lclient: genshin.Client):
#     items = await lclient.get_genshin_gacha_items()
#     assert items[0].is_character()
#     assert not items[-1].is_character()
