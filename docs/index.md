# genshin.py

Modern API wrapper for HoYoLAB & Miyoushe(米游社) API built on asyncio and pydantic.

---

Documentation: <https://seriaati.github.io/genshin.py>

API Reference: <https://seriaati.github.io/genshin.py/pdoc/genshin>

Source Code: <https://github.com/seriaati/genshin.py>

---

The primary focus of genshin.py is convenience. The entire project is fully type-hinted and abstracts a large amount of the api to be easier to use.

Key features:

- All data is in the form of Pydantic Models which means full autocompletion and linter support.
- Requests are significantly faster thanks to proper usage of asyncio.
- Chinese and English names returned by the API are renamed to simpler English fields.
- Supports the majority of the popular endpoints.
- Cleanly integrates with frameworks like FastAPI out of the box.

> Note: This library is a successor to [genshinstats](https://github.com/seriaati/genshinstats) - an unofficial wrapper for the Genshin Impact api.

## Requirements

- Python 3.9+
- aiohttp 3.0+
- Pydantic 2.0+
- tenacity 9.0+

## Installation

To install the stable version:

```console
pip install genshin
```

You can also install the latest development version from GitHub:

```console
pip install git+https://github.com/seriaati/genshin.py
```

A new release is made every 2 weeks.

## Example

A very simple example of how genshin.py would be used:

```py
import asyncio
import genshin

async def main():
    cookies = {"ltuid": 119480035, "ltoken": "cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT"}
    client = genshin.Client(cookies, uid=710785423)

    user = await client.get_genshin_user()
    print(f"User has a total of {len(user.stats.characters)} characters")

asyncio.run(main())
```
