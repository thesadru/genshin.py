# Chinese API

The chinese version of Genshin Impact uses a different API dubbed <abbr title='"miyoushe" - Chinese version of hoyolab'>米游社</abbr>. Since the API significantly differs from the overseas one you must create a separate client for it.

The Chinese client has almost the exact same usage, only the internals differ.

## Quick Example

```py
client = genshin.ChineseClient({"ltuid": ..., "ltoken": ...})

user = await client.get_user(101322963)
```

## Optimizations

The daily reward claiming for chinese players is a bit different, it requires a uid of one of the user's genshin accounts. Genshin.py is able to get it by itself but you may want to set it yourself if you know it.

```py
reward = await client.claim_daily_reward(101322963)
```