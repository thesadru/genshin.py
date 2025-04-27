import genshin


async def test_notes(zzz_client: genshin.Client):
    data = await zzz_client.get_zzz_notes()
    assert data


async def test_diary(zzz_client: genshin.Client):
    data = await zzz_client.get_zzz_diary()
    assert data


async def test_user(zzz_client: genshin.Client):
    data = await zzz_client.get_zzz_user()
    assert data


async def test_agents(zzz_client: genshin.Client):
    data = await zzz_client.get_zzz_agents()
    assert data


async def test_bangboos(zzz_client: genshin.Client):
    data = await zzz_client.get_bangboos()
    assert data


async def test_zzz_agent_info(zzz_client: genshin.Client):
    data = await zzz_client.get_zzz_agent_info(1011)
    assert data


async def test_shiyu_defense(zzz_client: genshin.Client):
    data = await zzz_client.get_shiyu_defense()
    assert data


async def test_deadly_assault(zzz_client: genshin.Client):
    data = await zzz_client.get_deadly_assault()
    assert data


async def test_lost_void_summary(zzz_client: genshin.Client):
    data = await zzz_client.get_lost_void_summary()
    assert data
