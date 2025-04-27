import genshin


async def test_notes(hsr_client: genshin.Client):
    data = await hsr_client.get_starrail_notes()
    assert data


async def test_user(hsr_client: genshin.Client):
    data = await hsr_client.get_starrail_user()
    assert data


async def test_characters(hsr_client: genshin.Client):
    data = await hsr_client.get_starrail_characters()
    assert data


async def test_challenge(hsr_client: genshin.Client):
    data = await hsr_client.get_starrail_challenge()
    assert data


async def test_rogue(hsr_client: genshin.Client):
    data = await hsr_client.get_starrail_rogue()
    assert data


async def test_pure_fiction(hsr_client: genshin.Client):
    data = await hsr_client.get_starrail_pure_fiction()
    assert data


async def test_apc_shadow(hsr_client: genshin.Client):
    data = await hsr_client.get_starrail_apc_shadow()
    assert data


async def test_event_calendar(hsr_client: genshin.Client):
    data = await hsr_client.get_starrail_event_calendar()
    assert data
