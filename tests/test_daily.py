import calendar
from datetime import datetime

import pytest
from genshin import GenshinClient


@pytest.mark.asyncio
async def test_daily_reward(lclient: GenshinClient):
    signed_in, claimed_rewards = await lclient.get_reward_info()
    reward = await lclient.claim_daily_reward()

    if signed_in:
        assert reward is None
    else:
        assert reward is not None

        rewards = await lclient.get_monthly_rewards()
        assert rewards[claimed_rewards].name == reward.name


@pytest.mark.asyncio
async def test_daily_reward_info(lclient: GenshinClient):
    s, c = await lclient.get_reward_info()
    assert isinstance(s, bool)
    assert isinstance(c, int)


@pytest.mark.asyncio
async def test_monthly_rewards(lclient: GenshinClient):
    rewards = await lclient.get_monthly_rewards()
    now = datetime.now()
    assert len(rewards) == calendar.monthrange(now.year, now.month)[1]


@pytest.mark.asyncio
async def test_claimed_rewards(lclient: GenshinClient):
    claimed = await lclient.claimed_rewards(limit=10).flatten()
