# Battle Chronicle

The main feature of genshin.py is the [Battle Chronicle](https://webstatic-sea.hoyolab.com/app/community-game-records-sea/index.html#/ys). It contains various features such as statistics, character equipment, spiral abyss runs, exploration progress, etc.

To request any of the Battle Chronicle endpoints you must first be logged in. Refer to [the authentication section](authentication.md) for more information.

## Quick example

```py
# get general user info:
user = await client.get_user(710785423)

# get spiral abyss runs:
data = await client.get_spiral_abyss(710785423, previous=True)

# get activities:
data = await client.get_activities(710785423)
```

## Real-Time Notes

Thanks to a relatively new feature added to battle chronicles you may now view your own resin count, explorations, comissions and similar data just using the API.

Currently you may only get your own data using your own cookies but a uid is still required.

```py
notes = await client.get_notes(710785423)
print(f"Resin: {notes.current_resin}/{notes.max_resin}")
print(f"Comissions: {notes.completed_comissions}/{notes.max_comissions}")
```

## Optimizations

Under the hood, `get_user` has to make two requests: one for the user and another for character equipment. If you do not care about character equipment, you should use `get_partial_user`.

```py
user = await client.get_partial_user(710785423)
print(user.stats.days_active)
```

On the other hand, if you want to request as much information as possible, you should use `get_full_user` which adds spiral abyss runs and activities to the user.

```py
user = await client.get_full_user(710785423)
print(user.abyss.previous.total_stars)
```

If you only want to get character data, you may batch-request characters using a uid and a list of character ids. You may want to utilize `genshin.CHARACTER_NAMES` to get the ids.
```py
character_ids = [10000006, 10000014, 10000015, 10000021]
characters = await client.get_characters(710785423, character_ids)
print(characters[0].name)
```

By default, when requesting data of another user, `get_user` returns only their 8 most used characters. You may provide `character_ids` to also request more users. 

In case you want to find out what all characters a user has you may get the ids by bruteforcing every single possible character id by setting `all_characters=True`. This is of course incredibly slow and you are therefore encouraged to cache the character ids in a database.
```py
# get all of these character ids in addition to the 8 most used characters
user = await client.get_user(710785423, character_ids=[10000006, 10000014, 10000015, 10000021])

# get all characters a user has (makes a large amount of requests)
user = await client.get_user(710785423, all_charactersTrue)
character_ids = [c.id for c in user.characters] # remember to cache these!
```
