import pytest

import genshin


async def test_game_accounts(lclient: genshin.Client):
    data = await lclient.get_game_accounts()

    assert data


async def test_search(client: genshin.Client, hoyolab_id: int):
    users = await client.search_users("sadru")

    for user in users:
        if user.hoyolab_id == hoyolab_id:
            break
    else:
        raise AssertionError("Search did not return the correct users")

    assert user.nickname == "sadru"


async def test_hoyolab_user(client: genshin.Client, hoyolab_id: int):
    user = await client.get_hoyolab_user(hoyolab_id)

    assert user.nickname == "sadru"


async def test_recommended_users(client: genshin.Client):
    users = await client.get_recommended_users()

    assert len(users) > 80


async def test_announcements(client: genshin.Client):
    announcements = await client.get_genshin_announcements()

    assert len(announcements) > 10


async def test_redeem_code(lclient: genshin.Client):
    try:
        await lclient.redeem_code("GENSHINGIFT")
    except genshin.RedemptionException as e:
        pytest.skip(f"Redemption code is inconsistent: {e}")
    except genshin.AccountNotFound:
        pytest.skip("No genshin account.")


async def test_starrail_redeem_code(lclient: genshin.Client):
    try:
        await lclient.redeem_code("HSRGRANDOPEN1", game=genshin.types.Game.STARRAIL)
    except genshin.RedemptionException:
        pytest.skip("Redemption code is inconsistent again.")
    except genshin.AccountNotFound:
        pytest.skip("No star rail account.")


async def test_check_in_community(lclient: genshin.Client):
    try:
        await lclient.check_in_community()
    except genshin.GenshinException as e:
        if e.retcode != 2001:
            raise
