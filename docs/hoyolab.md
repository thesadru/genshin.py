# Hoyolab

Since the api genshin.py is requesting is made primarily for [hoyolab](https://www.hoyolab.com/) some minor utility functions related to it are also supported.

## Quick example

```py
# get the uid, nickname and level of a user from a hoyolab uid
card = await client.get_record_card(8366222)
print(card.uid, card.level, card.nickname)
```

```py
# list of all game accounts of the currently logged-in user
accounts = await client.get_game_accounts()
for account in accounts:
    print(account.uid, account.level, account.nickname)
```

```py
# redeem a gift code for the currently logged-in user
await client.redeem_code("GENSHINGIFT")
```

```py
# search users
users = await client.search_users("sadru")
print(users[0].hoyolab_id)

# get a list of random recommended users (useful for data gathering)
users = await client.get_recommended_users()
print(users[0].hoyolab_id)

# to actually get any useful data:
card = await client.get_record_card(users[0].hoyolab_id)
```
