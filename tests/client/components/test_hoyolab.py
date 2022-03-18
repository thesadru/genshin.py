import genshin


async def test_game_accunts(lclient: genshin.Client):
    data = await lclient.get_game_accounts()

    assert data
