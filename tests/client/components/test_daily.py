import calendar
import datetime

import genshin

CN_TIMEZONE = datetime.timezone(datetime.timedelta(hours=8))


async def test_daily_reward(lclient: genshin.Client):
    signed_in, claimed_rewards = await lclient.get_reward_info()

    try:
        reward = await lclient.claim_daily_reward()
    except genshin.AlreadyClaimed:
        assert signed_in
        return
    else:
        assert not signed_in

    rewards = await lclient.get_monthly_rewards()
    assert rewards[claimed_rewards].name == reward.name


async def test_starrail_daily_reward(lclient: genshin.Client):
    signed_in, claimed_rewards = await lclient.get_reward_info(game=genshin.types.Game.STARRAIL)

    try:
        reward = await lclient.claim_daily_reward(game=genshin.types.Game.STARRAIL)
    except genshin.AlreadyClaimed:
        assert signed_in
        return
    else:
        assert not signed_in

    rewards = await lclient.get_monthly_rewards(game=genshin.types.Game.STARRAIL)
    assert rewards[claimed_rewards].name == reward.name


async def test_monthly_rewards(lclient: genshin.Client):
    rewards = await lclient.get_monthly_rewards()
    now = datetime.datetime.now(CN_TIMEZONE)
    assert len(rewards) == calendar.monthrange(now.year, now.month)[1]


async def test_claimed_rewards(lclient: genshin.Client):
    claimed = await lclient.claimed_rewards(limit=10).flatten()
    assert claimed[0].time <= datetime.datetime.now().astimezone()
