# Configuration

## Language

The API supports several languages. You can set what language you want the response to be in by either changing the client language `client.lang` or passing the language as a method argument.

The default language is `en-us` for overseas and `zh-cn` for china.

```py
client = genshin.Client(lang="fr-fr")
# or
client = genshin.Client()
user = await client.get_genshin_user(710785423, lang="zh-cn")
```

### Supported Languages

| Code  | Language   |
| ----- | ---------- |
| de-de | Deutsch    |
| en-us | English    |
| es-es | Español    |
| fr-fr | Français   |
| id-id | Indonesia  |
| ja-jp | 日本語     |
| ko-kr | 한국어     |
| pt-pt | Português  |
| ru-ru | Pусский    |
| th-th | ภาษาไทย    |
| vi-vn | Tiếng Việt |
| zh-cn | 简体中文   |
| zh-tw | 繁體中文   |

> This mapping is contained in `genshin.LANGS`

### Character Name Language

Some genshin endpoints fail to return character names. Genshin.py therefore fetches character names from a 3rd party database.
By default the [enka repository](https://github.com/EnkaNetwork/API-docs/) is used but others can be chosen.
These functions only need to be ran once on startup.

| Function                                                | Source                                                   | Notes                                                                                           |
| ------------------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `await genshin.utility.update_characters_genshindata()` | [GenshinData](https://github.com/Dimbreath/GenshinData/) | Source of data for all other 3rd party services, has to downloads >20MB per language to be used |
| `await genshin.utility.update_characters_enka()`        | [EnkaNetwork](https://github.com/EnkaNetwork/API-docs/)  | Repository updates take a while, not reliable right after a genshin update                      |
| `await genshin.utility.update_characters_ambr()`        | [Project Amber](https://ambr.top/)                       | Uses a 3rd party API that may be subject to change, does a unique request for every language    |

## Cookie Manager

By default `Client` uses a single cookie. This behavior may be changed by overwriting `client.cookie_manager` with a subclass of `BaseCookieManager`.

For convenience, if a list of cookies is passed into `Client.set_cookies` the cookie manager will be automatically set to `genshin.RotatingCookieManager`.

### Example

```py
import genshin

class RandomCookieManager(genshin.BaseCookieManager):
    """Cookie Manager that provides random cookies fetched from a database."""

    def __init__(self, database):
        self.database = database

    async def request(self, url, *, method = "GET", **kwargs):
        cookies = await self.database.get_random_cookies()
        return await self._request(method, url, cookies=cookies, **kwargs)

```

### International Cookie Manager

When providing data for both cn and os players you might want to share the same client for them and in extension things like the cache. To achieve that you have to set cookies for all regions with `InternationalCookieManager`.

```py

client.cookie_manager = genshin.InternationalCookieManager({
    genshin.Region.OVESEAS: [{...}, ...],
    genshin.Region.CHINESE: [{...}, ...],
})
```

## Cached UIDs

Some endpoints require a uid despite being private. Genshin.py chooses to fetch and cache these uids instead of forcing users to provide it themselves.
This may however cause some obvious performance issues, so it is recommended to set the uids yourself in case you cannot afford to always have an extra delay when creating a new client.

```py
client = genshin.Client(game=genshin.Game.GENSHIN)

client.uid = 710785423
```

You can set a UID for a specific game if there's no default game set.

```py
client.uids[genshin.Game.GENSHIN] = 710785423
client.uids[genshin.Game.HONKAI] = 200476231
```

## Default Region

By default all requests will be assumed to be meant to be used with overseas cookies.
If you wish to use chinese cookies and chinese endpoints you must change the default region.

```py
client = genshin.Client(region=genshin.Region.CHINESE)

client.region = genshin.Region.CHINESE
```

## Default Game

Some endpoints may be the exact same for both genshin and honkai so they require a game to be specified. This can be also done by setting a default game for the client.

```py
client = genshin.Client(game=genshin.Game.HONKAI)

client.default_game = genshin.Game.HONKAI
```

## Proxy

Some endpoints may block chinese IPs. Setting up a proxy in this case is recommended.

For more information, [check out the aiohttp docs](https://docs.aiohttp.org/en/stable/client_advanced.html#proxy-support).

```py
client = genshin.Client(proxy="http://127.0.0.1:1080")

client.proxy = "http://127.0.0.1:1080"
```
