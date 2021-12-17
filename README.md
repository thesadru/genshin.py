# Fork-specific stuff (revert before possible merge)

Very much WIP branch focused on adding the new Honkai Impact Hoyolab API endpoints to genshin.py.  
Currently on the agenda:
- Extract generic `GenshinClient` functionality that applies to to entirety of Hoyolab into a new base Client,
- Add a HonkaiClient that derives from said new generic Client,
- Add new Pydantic Models to parse the data returned by the Honkai Impact side into a more useable format,
- Add sufficient tests for all the changes (more like learn pytest altogether :/),
- Somehow convince Sadru that the code is good enough for a merge.

For now, while the extracting is still WIP, raw Honkai player data requests can be done as follows:
```py
client = GenshinClient()
client.set_cookies(ltuid="<my_ltuid>", ltoken="<my_ltoken>")

await client.request_game_record(
    "honkai3rd/api/<endpoint>",
    params={"server": "<my_server>", "role_id": "<my_honkai_UID>"}
)
```
> _Note: this code snippet is not complete, and will not run as-is (except in an iPython kernel/Jupyter notebook, etc.)_

...with any of the following endpoints (listed as endpoint name ~ Hoyolab website equivalent, respectively):
```
index             ~ Summary
characters        ~ My valkyries
godWar            ~ Elysian Realm
newAbyssReport    ~ Abyss Report
battleFieldReport ~ Arena Report
```
Please see the [extra/honkai_example.py](https://github.com/Chromosomologist/genshin.py/blob/master/extra/honkai_example.py) for a quick example on how the current (limited, WIP) implementation can be used to parse the returned data. Of course, keep in mind that this will be streamlined to work exactly the same as the current `GenshinClient` implementation.

The original readme will continue below.

---

# genshin.py
Modern API wrapper for ~~Genshin Impact~~ Hoyolab built on asyncio and pydantic.

---

Documentation: https://thesadru.github.io/genshin.py

Source Code: https://github.com/thesadru/genshin.py

---

The primary focus of genshin.py is convenience. The entire project is fully type-hinted and abstracts a large amount of the api to be easier to use.

Key features:

* All data is in the form of Pydantic Models which means full autocompletion and linter support.
* Requests are significantly faster thanks to proper usage of asyncio.
* Chinese and Engrish names returned by the API are renamed to simpler English fields.
* Supports the majority of the popular endpoints.
* Cleanly integrates with frameworks like FastAPI out of the box.

> Note: This library is a successor to [genshinstats](https://github.com/thesadru/genshinstats) - an unofficial wrapper for the Genshin Impact api.

## Requirements
- Python 3.8+
- aiohttp
- Pydantic

```console
pip install genshin
```

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

## Contributing
Any kind of contribution is welcome.

Before making a pull request remember to test your changes using pytest.
Remember to set your `LTUID` and `LTOKEN` environment variables.
```
pip install genshin[test]
python -m pytest
```

Please also edit the documentation accordingly. You may see how the final documentation would look like by starting an `mkdocs` server.
```
pip install genshin[doc]
mkdocs serve
```
