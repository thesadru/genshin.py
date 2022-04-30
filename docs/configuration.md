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
