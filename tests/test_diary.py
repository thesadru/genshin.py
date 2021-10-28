import datetime

import pytest
from genshin import GenshinClient


@pytest.mark.asyncio
async def test_diary(lclient: GenshinClient, uid: int):
    diary = await lclient.get_diary()
    assert diary.uid == uid == lclient.uid
    assert diary.nickname == "sadru"
    assert diary.month == datetime.datetime.now().month
    assert diary.data.current_mora > 0


@pytest.mark.asyncio
async def test_diary_log(lclient: GenshinClient, uid: int):
    log = lclient.diary_log(limit=10)
    data = await log.flatten()

    assert data[0].amount > 0

    assert log.data.uid == uid == lclient.uid
    assert log.data.nickname == "sadru"
    assert log.data.month == datetime.datetime.now().month
