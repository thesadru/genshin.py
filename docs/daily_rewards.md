# Daily Rewards

Since hoyo forces users to claim their daily rewards through the website we can abuse that system and claim rewards automatically.

To request any of the Battle Chronicle endpoints you must first be logged in. Refer to [the authentication section](authentication.md) for more information.

These endpoints require a game to be specified. It's best to [configure the default game](configuration.md#default-game) or use the `game=` parameter.

## Quick Example

```py
# claim daily reward
try:
    reward = await client.claim_daily_reward()
except genshin.AlreadyClaimed:
    print("Daily reward already claimed")
else:
    print(f"Claimed {reward.amount}x {reward.name}")
```

```py
# get all claimed rewards
async for reward in client.claimed_rewards():
    print(f"{reward.time} - {reward.amount}x {reward.name}")
```

```py
# get info about the current daily reward status
signed_in, claimed_rewards = await client.get_reward_info()
print(f"Signed in: {signed_in} | Total claimed rewards: {claimed_rewards}")
```

## Optimizations

Under the hood, `client.claim_daily_reward` makes an additional request to get the claimed reward. If you don't want that you may disable the extra request with `client.claim_daily_reward(reward=False)`
