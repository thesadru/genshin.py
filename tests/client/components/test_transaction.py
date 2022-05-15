import genshin


async def test_transactions(lclient: genshin.Client, authkey: str):
    log = await lclient.transaction_log("resin", limit=20)
    assert log[0].kind == "resin"
    assert log[0].get_reason_name() != str(log[0].reason_id)


async def test_merged_transactions(lclient: genshin.Client, authkey: str):
    async for trans in lclient.transaction_log(limit=30):
        if trans.kind in ("primogem", "crystal", "resin"):
            assert not hasattr(trans, "name")
        else:
            assert hasattr(trans, "name")
