import pytest

from genshin import GenshinClient


@pytest.mark.asyncio
async def test_transactions(lclient: GenshinClient):
    log = await lclient.transaction_log("resin", limit=30).flatten()
    assert log[0].kind == "resin"


@pytest.mark.asyncio
async def test_merged_transactions(lclient: GenshinClient):
    async for trans in lclient.transaction_log(limit=30):
        assert trans.reason

        if trans.kind in ("primogem", "crystal", "resin"):
            assert not hasattr(trans, "name")
        else:
            assert hasattr(trans, "name")


@pytest.mark.asyncio
async def test_filtered_merged_transactions(lclient: GenshinClient):
    async for trans in lclient.transaction_log(["artifact", "weapon"], limit=20):
        assert trans.kind in ["artifact", "weapon"]
