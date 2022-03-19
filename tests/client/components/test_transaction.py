import genshin


async def test_transactions(lclient: genshin.Client):
    log = await lclient.transaction_log("resin", limit=20)
    assert log[0].kind == "resin"


async def test_merged_transactions(lclient: genshin.Client):
    async for trans in lclient.transaction_log(limit=30):
        if trans.kind in ("primogem", "crystal", "resin"):
            assert not hasattr(trans, "name")
        else:
            assert hasattr(trans, "name")
