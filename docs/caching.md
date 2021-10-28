# Caching

Genshin.py uses several caches:

- `client.cache` - A standard cache for http requests
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

## Custom caches

Sometimes a simple mutable mapping won't do, for example with redis caches. In this case you can overwrite the caching methods of `GenshinClient`

Example with aioredis:

```py
import aioredis
import genshin


class RedisClient(genshin.GenshinClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.redis = aioredis.from_url("redis://localhost")

    async def _check_cache(self, key, check, lang):
        """Check the cache for any entries"""
        key = ":".join(map(str, key + (lang or self.lang,)))

        data = self.redis.get(key)
        if data is None:
            return None

        if check is None or check(data):
            return data

        self.redis.delete(key)

        return None

    async def _update_cache(self, data, key, check=None, lang=None) -> None:
        """Update the cache with a new entry"""
        key = ":".join(map(str, key + (lang or self.lang,)))

        if check is not None and not check(data):
            return

        self.redis.set(key, data, ex=3600)
```
