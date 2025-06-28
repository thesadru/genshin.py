import pytest

import genshin


async def test_record_cards(client: genshin.Client, hoyolab_id: int):
    data = await client.get_record_cards(hoyolab_id)

    assert data

    assert data[0].level >= 40


async def test_genshin_user(client: genshin.Client, genshin_uid: int):
    data = await client.get_genshin_user(genshin_uid)

    assert data


async def test_genshin_detailed_characters(client: genshin.Client, genshin_uid: int):
    data = await client.get_genshin_detailed_characters(genshin_uid)

    assert data


async def test_partial_genshin_user(client: genshin.Client, genshin_uid: int):
    data = await client.get_partial_genshin_user(genshin_uid)

    assert data


async def test_spiral_abyss(client: genshin.Client, genshin_uid: int):
    data = await client.get_spiral_abyss(genshin_uid, previous=True)

    assert data


async def test_imaginarium_theater(client: genshin.Client, genshin_uid: int):
    data = await client.get_imaginarium_theater(genshin_uid)

    assert data


async def test_notes(lclient: genshin.Client, genshin_uid: int):
    data = await lclient.get_notes(genshin_uid)

    assert data

    if td := data.remaining_transformer_recovery_time:
        assert sum(1 for i in (td.days, td.hours, td.minutes, td.seconds) if i) == 1


async def test_genshin_activities(client: genshin.Client, genshin_uid: int):
    data = await client.get_activities(genshin_uid)

    assert data


async def test_genshin_tcg(lclient: genshin.Client, genshin_uid: int):
    data = await lclient.genshin_tcg(limit=64)

    assert data


async def test_full_genshin_user(client: genshin.Client, genshin_uid: int):
    data = await client.get_full_genshin_user(genshin_uid)

    assert data


async def test_exceptions(client: genshin.Client):
    with pytest.raises(genshin.DataNotPublic):
        await client.get_record_cards(10000000)


async def test_envisaged_echoes(client: genshin.Client, genshin_uid: int):
    echoes = await client.get_envisaged_echoes(genshin_uid)
    assert echoes


async def test_stygian_onslaught(client: genshin.Client, genshin_uid: int):
    data = await client.get_stygian_onslaught(genshin_uid)
    assert data


async def test_raw_stygian_onslaught(client: genshin.Client, genshin_uid: int):
    data = await client.get_stygian_onslaught(genshin_uid, raw=True)
    assert data
