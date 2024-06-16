import datetime

import genshin


async def test_diary(lclient: genshin.Client, genshin_uid: int):
    diary = await lclient.get_diary()
    assert diary.uid == genshin_uid == lclient.uids[genshin.Game.GENSHIN]
    assert diary.month == datetime.datetime.now().month
    assert diary.data.current_mora >= 0


async def test_diary_log(lclient: genshin.Client, genshin_uid: int):
    log = lclient.diary_log(limit=10)
    data = await log.flatten()

    if data:
        assert data[0].amount > 0

    assert log.data.uid == genshin_uid == lclient.uids[genshin.Game.GENSHIN]
    assert log.data.month == datetime.datetime.now().month
