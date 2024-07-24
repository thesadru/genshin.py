import genshin


async def test_lineup_fields(client: genshin.Client):
    data = await client.get_lineup_fields()

    assert data


async def test_lineup_scenarios(client: genshin.Client):
    data = await client.get_lineup_scenarios()

    assert data


async def test_lineups(client: genshin.Client):
    data = await client.get_lineups(limit=10, page_size=10, characters=[10000002])

    assert data


async def test_lineup_details(client: genshin.Client):
    data = await client.get_lineup_details("6358a87a30ad88f7465475e9")

    assert data


async def test_user_lineups(lclient: genshin.Client):
    await lclient.get_user_lineups()


async def test_favorite_lineups(lclient: genshin.Client):
    await lclient.get_favorite_lineups()


async def test_lineup_character_history(lclient: genshin.Client):
    data = await lclient.get_lineup_character_history()

    assert len(data) < 100
