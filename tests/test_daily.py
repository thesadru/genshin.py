import calendar
from datetime import datetime

import pytest
from genshin import GenshinClient, GenshinException, AlreadyClaimed


@pytest.mark.asyncio_cooperative
async def test_daily_reward(lclient: GenshinClient):
    try:
        signed_in, claimed_rewards = await lclient.get_reward_info()
    except GenshinException as e:
        if e.retcode == -1004:
            return pytest.skip("Daily rewards are ratelimited")
        raise

    try:
        reward = await lclient.claim_daily_reward()
    except AlreadyClaimed:
        assert signed_in
    else:
        assert not signed_in

        rewards = await lclient.get_monthly_rewards()
        assert rewards[claimed_rewards].name == reward.name


@pytest.mark.asyncio_cooperative
async def test_monthly_rewards(lclient: GenshinClient):
    rewards = await lclient.get_monthly_rewards()
    now = datetime.now()
    assert len(rewards) == calendar.monthrange(now.year, now.month)[1]


@pytest.mark.asyncio_cooperative
async def test_claimed_rewards(lclient: GenshinClient):
    claimed = await lclient.claimed_rewards(limit=10).flatten()
    assert claimed[0].time <= datetime.now()
