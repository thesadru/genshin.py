import contextlib

import genshin


async def test_game_accounts(lclient: genshin.Client):
    data = await lclient.get_game_accounts()

    assert data


async def test_search(client: genshin.Client, hoyolab_uid: int):
    users = await client.search_users("sadru")

    for user in users:
        if user.hoyolab_uid == hoyolab_uid:
            break
    else:
        raise AssertionError("Search did not return the correct users")

    assert user.nickname == "sadru"


async def test_recommended_users(client: genshin.Client):
    users = await client.get_recommended_users()

    assert len(users) > 80


async def test_redeem_code(lclient: genshin.Client):
    # inconsistent
    with contextlib.suppress(genshin.RedemptionClaimed):
        await lclient.redeem_code("genshingift")
