# genshin.py
Modern API wrapper for Genshin Impact built on asyncio and pydantic.

---

Documentation: https://thesadru.github.io/genshin.py

Source Code: https://github.com/thesadru/genshin.py

---

The primary focus of genshin.py is convenience. The entire project is fully type-hinted and abstracts a large amount of the api to be easier to use.

Key features:

* All data is in the form of <abbr title="Practically glorified dataclasses with builtin validation">Pydantic Models</abbr> which means full autocompletion and linter support.
* Requests are significantly faster thanks to proper usage of asyncio.
* Chinese and engrish names returned by the api are renamed to simpler english fields.
* Supports the majority of the most used endpoints.
* Cleanly integrates with frameworks like fastapi out of the box.

## Requirements
- Python 3.8+
- aiohttp
- Pydantic

```console
pip install genshin
```

## Example

A very simple example of how genshin.py would be used
```py
import asyncio
import genshin

async def main():
    cookies = {"ltuid": 119480035, "ltoken": "cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT"}
    client = genshin.GenshinClient(cookies)

    data = await client.get_user(710785423)
    print(f"User has a total of {len(data.characters)} characters")

    # remember to close the client so you don't leave a hanging aiohttp session
    await client.close()

asyncio.run(main())
```
