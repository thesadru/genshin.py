# Battle Chronicle

The main feature of genshin.py is the [Battle Chronicle](https://webstatic-sea.hoyolab.com/app/community-game-records-sea/index.html#/ys). It contains various features such as statistics, character equipment, spiral abyss runs, exploration progress, etc.

To request any of the Battle Chronicle endpoints you must first be logged in. Refer to [the authentication section](authentication.md) for more information.

## Quick example

```py
# get general user info:
user = await client.get_genshin_user(710785423)
user = await client.get_honkai_user(710785423)

# get abyss:
data = await client.get_spiral_abyss(710785423, previous=True)
data = await client.get_honkai_abyss(710785423)
```

## Optimizations

Some methods implicitly make multiple requests at once:

- instead of `get_genshin_user` you can use `get_partial_genshin_user` and `get_characters`
- instead of `get_honkai_abyss` you can use `get_old_abyss` or `get_superstring_abyss`

```py
user = await client.get_partial_genshin_user(710785423)
print(user.stats.days_active)
```

On the other hand, if you want to request as much information as possible, you should use `get_full_genshin_user`/`get_full_honkai_user` which adds spiral abyss runs and activities to the user.

```py
user = await client.get_full_genshin_user(710785423)
print(user.abyss.previous.total_stars)
```
