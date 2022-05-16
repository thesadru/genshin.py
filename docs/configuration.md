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

Some genshin endpoints fail to return character names. Genshin.py will attempt to guess them from their icons and IDs, however this behavior by default only works in English.
To modify this behavior you must either overwrite `genshin.models.CHARACTER_NAMES` or run `client.update_character_names()` with the appropriate language.

> Note that this only works with one language at a time. Once support for multiple languages is added all of this will be done implicitly for you.

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

## Proxy Support

Some endpoints may block your IP, you can set up a proxy, aiohttp only support `http/https/ws/wss` proxy for now.

For more information, check https://docs.aiohttp.org/en/stable/client_advanced.html

```py
client = genshin.Client(proxy="http://127.0.0.1:1080")
# or
client = genshin.Client()
client.proxy = "http://127.0.0.1:1080"

# Clear Proxy Setting
client.proxy = None
```
