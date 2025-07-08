# Fetching HSR Characters

Normally, you would do:

```py
client = genshin.Client(cookies)
await client.get_starrail_characters()
```

However, when you view another user's profile, the following things are not available:

- Character's traces
- Character's properties/stats
- Properties of the character's relics and ornaments
- Memosprite information

In this case, the normal model parsing for detailed character information will fail and raise an error. To avoid this, pass in the `simple` parameter as `True`:

```py
client = genshin.Client(cookies)
await client.get_starrail_characters(uid=other_players_uid, simple=True)
```
