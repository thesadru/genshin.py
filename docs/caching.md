# Caching

Genshin.py caches data for you using a custom `genshin.BaseCache` object in `client.cache`.

## Quick example

```py
# create a cache
client = genshin.Client()
client.set_cache(maxsize=256, ttl=3600)

# set a custom cache
client.cache = genshin.StaticCache()
```

## Custom caches

Sometimes a simple mutable mapping won't do, for example with redis caches. In this case you can overwrite the cache with your own.

Example:

```py
import json
import typing

import genshin

class JsonCache(genshin.BaseCache):
    """Terrible json cache without any expiration."""

    def __init__(self, filename) -> None:
        self.filename = filename

    async def get(self, key):
        with open(self.filename, "r") as file:
            data = json.load(file)

        return data.get(str(key))

    async def set(self, key, value) -> None:
        with open(self.filename, "r") as file:
            data = json.load(file)

        data[str(key)] = value

        with open(self.filename, "w") as file:
            json.dump(data, file)

    async def get_static(self, key):
        return await self.get(key)

    async def set_static(self, key, value) -> None:
        await self.set(key, value)


client.cache = JsonCache("cache.json")
```

### Redis cache

A redis cache is provided by default with `RedisCache`. It is recommended to overwrite this class and modify the serialization methods since normal json may prove to be a bit too slow.

```py
import aioredis

client.cache = genshin.RedisCache(aioredis.Redis(...))
```
