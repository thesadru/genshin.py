# Caching

Genshin.py uses several caches:

- `client.cache` - A standard cache for http requests
- `client.redis_cache` - A redis cache for http requests
- `client.paginator_cache` - A cache for individual paginator
- `client.static_cache` - A cache for static resources

It is recommended to use `cachetools` to set your caches. Genshin.py has a builtin utility method to create caches for you.

## Installation
```console
pip install genshin[cache]
```

## Quick example

```py
# create a cache with a specific strategy
client = genshin.GenshinClient()
client.set_cache(maxsize=256, strategy="LRU")

import cachetools
client = genshin.GenshinClient()
client.cache = cachetools.FIFOCache(16)

# create a ttl cache with a 1h lifespan
client = genshin.GenshinClient()
client.set_cache(maxsize=256, ttl=3600)
```

## Paginator caches

A paginator cache is used for wish history and transactions. The mapping used for this paginator must support frequent access since every single individual item will be stored separately for optimization.
```py
import cachetools

client = genshin.GenshinClient()
client.paginator_cache = LRUCache(2048) # A simple LRU cache is ideal
```

## Static caches

Every request towards a static endpoint is cached. You may overwrite it with any other mapping but unless you're only trying to make the caching persistent there's generally no reason to.
```py
client = genshin.GenshinClient()
items = await client.get_gacha_items()
print(len(client.static_cache))
```

## Redis caches

Not always is an in-memory cache sufficient. Genshin.py therefore has native support for redis caches. 
Redis caches are powered by [aioredis](https://aioredis.readthedocs.io/en/latest/)

```py
client = genshin.GenshinClient()
# same arguments you would pass into "aioredis.from_url"
client.set_redis_cache("redis://localhost", username="user", password="pass")
```