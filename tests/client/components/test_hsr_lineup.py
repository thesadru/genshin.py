import genshin


async def test_game_modes(hsr_client: genshin.Client):
    game_modes = await hsr_client.get_starrail_lineup_game_modes()
    assert len(game_modes) >= 3


async def test_lineups(hsr_client: genshin.Client):
    lineups = await hsr_client.get_starrail_lineups(tag_id=18, group_id=2014, type="pf")
    assert len(lineups.lineups) > 0
    assert lineups.next_page_token is not None


async def test_lineups_next_page(hsr_client: genshin.Client):
    lineups = await hsr_client.get_starrail_lineups(tag_id=18, group_id=2014, type="pf")
    next_page = await hsr_client.get_starrail_lineups(
        tag_id=18, group_id=2014, type="pf", next_page_token=lineups.next_page_token
    )
    assert len(next_page.lineups) > 0


async def test_lineups_moc(hsr_client: genshin.Client):
    lineups = await hsr_client.get_starrail_lineups(tag_id=14, group_id=1023, type="moc")
    assert len(lineups.lineups) > 0
    assert lineups.next_page_token is not None


async def test_lineups_pf(hsr_client: genshin.Client):
    lineups = await hsr_client.get_starrail_lineups(tag_id=18, group_id=2014, type="pf")
    assert len(lineups.lineups) > 0
    assert lineups.next_page_token is not None
    assert lineups.lineups[0].detail.buffs is not None
    assert lineups.lineups[0].detail.buffs[0].name is not None


async def test_lineups_apc(hsr_client: genshin.Client):
    lineups = await hsr_client.get_starrail_lineups(tag_id=24, group_id=3009, type="apc")
    assert len(lineups.lineups) > 0
    assert lineups.next_page_token is not None
    assert lineups.lineups[0].detail.buffs is not None
    assert lineups.lineups[0].detail.buffs[0].name is not None


async def test_moc_schedules(hsr_client: genshin.Client):
    schedules = await hsr_client.get_starrail_lineup_schedules("moc")
    assert len(schedules) > 0


async def test_pf_schedules(hsr_client: genshin.Client):
    schedules = await hsr_client.get_starrail_lineup_schedules("pf")
    assert len(schedules) > 0


async def test_apc_schedules(hsr_client: genshin.Client):
    schedules = await hsr_client.get_starrail_lineup_schedules("apc")
    assert len(schedules) > 0
