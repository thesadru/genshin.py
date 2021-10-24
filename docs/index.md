# Overview
Modern API wrapper for Genshin Impact built on [asyncio](https://docs.python.org/3/library/asyncio.html) and [pydantic](https://pydantic-docs.helpmanual.io/).

The primary focus of genshin.py is convenience. The entire project is fully type-hinted and abstracts a large amount of the api to be easier to use.

Key features:

* All data is in the form of <abbr title="Improved dataclasses with built-in validation">Pydantic Models</abbr> which means full autocompletion and linter support.
* Requests are significantly faster thanks to proper usage of asyncio.
* Chinese and Engrish names returned by the API are renamed to simpler English fields.
* Supports the majority of the popular endpoints.
* Cleanly integrates with frameworks like FastAPI out of the box.

## Installation

From PyPI:
```console
pip install genshin
```
From github:
```console
pip install git+https://github.com/thesadru/genshin.py
```

### Requirements: 

- Python 3.8+
- aiohttp
- Pydantic



## Example

A very simple example of how genshin.py would be used:
```py
import asyncio
import genshin

async def main():
    cookies = {"ltuid": 119480035, "ltoken": "cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT"}
    client = genshin.GenshinClient(cookies)

    data = await client.get_user(710785423)
    print(f"User has a total of {len(data.characters)} characters")

    await client.close()

asyncio.run(main())
```
