# Wish History

Contains the wish history and banner details.

To request any of the wish history endpoints you must set an authkey. Refer to [the authentication section](authentication.md) for more information.

## Quick example

```py
# simply iterate over the wish history
async for wish in client.wish_history():
    print(f"{wish.time} - {wish.name} ({wish.rarity}* {wish.type})")

# set a limit for the iteration
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
# get wishes only from the permanent banner
async for wish in client.wish_history(200, limit=20):
    print(f"{wish.time} - {wish.name} ({wish.rarity}* {wish.type})")

# get wishes from both the character and the weapon banner
async for wish in client.wish_history([301, 302], limit=20):
    print(f"{wish.time} - {wish.name} ({wish.rarity}* {wish.type})")
```

## Banner Details

In the same way you can get data for your wish history you may also get data for the static banner details.

### Quick example

```py
# get all the current banners
banners = await client.get_banner_details()
for banner in banners:
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

`get_banner_details` requires ids to get the banner details. These ids change with every new banner so for user experience they are hosted on a remote repository maintained by me. In case you want to get proper data before I update the ids you may simply just get them yourself by openning every single details page in genshin and then running `genshin.get_banner_ids()`

```py
banner_ids = genshin.get_banner_ids()
banners = await client.get_banner_details(banner_ids)
```
