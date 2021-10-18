# Caching

Genshin.py uses a total of 3 caches:

- `client.cache` - A standard cache for http requests
- `client.paginator_cache` - A cache for individual paginator
- `client.static_cache` - A cache for static resources

It is recommended to use `cachetools` to set your caches. Genshin.py has a builtin utility method to create caches for you.

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

A paginator cache
