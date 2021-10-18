# Wish History

Contains the wish history and banner details.

To request any of the wish history endpoints you must set an authkey. Refer to [the authentication section](authentication.md) for more information.

## Quick example

```py
# simply iterate over the wish history
async for wish in client.wish_history(limit=100):
    print(f"{wish.time} - {wish.name} ({wish.rarity}* {wish.type})")

# get and flatten the wish history
history = await client.wish_history(limit=100).flatten()
print(history[-1].time)

# get the first wish in the paginator (most recent one)
wish = await client.wish_history().first()
print(wish.uid)
```

## Filtering data by banner

By default `client.wish_history()` gets data from all banners, you can filter the results by passing in a banner id. You may also call `client.get_banner_names()` to get the banner names in various languages.

| Banner               | ID  |
| -------------------- | --- |
| Novice Wishes        | 100 |
| Permanent Wish       | 200 |
| Character Event Wish | 301 |
| Weapon Event Wish    | 302 |

```py
async for wish in client.wish_history(200, limit=20):
    print(f"{wish.time} - {wish.name} ({wish.rarity}* {wish.type})")
```

## Banner Details

To get banner details you require the banner's id. Like authkeys, these can be gotten from the logfile. Simply open the banner page in genshin impact and then run `genshin.get_banner_ids()`

If you do not want to get the banner ids every time you may fetch them from a user-maintained storage using `client.fetch_banner_ids`

### Quick example

```py
# get all the current banners
banner_ids = await client.fetch_banner_ids()
for banner_id in banner_ids:
    banner = await client.get_banner_details(banner_id)
    print(banner.name)
```
```py
# get a list of all items that can be gotten from the gacha
items = await client.get_gacha_items()
```

## Optimizations

You may start from any point in the paginator as long as you know the id of the previous item.
```py
async for wish in client.wish_history(limit=20):
    print(wish)

async for wish in client.wish_history(limit=20, end_id=wish.id):
    print(wish)
```


When getting data from a single banner you may use the `next_page` method to get the next 20 items in the paginator.
```py
# a more accurate progress bar
history = client.wish_history(200)
while not history.exhausted:
    page = await history.next_page()
    print('.', end='')
```