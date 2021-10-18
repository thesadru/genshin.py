# Debugging

## Interactive console

Since genshin.py uses asyncio it's fairly hard to debug code in the interactive console. Instead I highly recommend you use [IPython](https://ipython.org/).

## Requests

Genshin.py automatically logs all requests using the `logging` module. You can make these logs show up in the console by setting the `debug` kwarg to `True`

```ipython
In [1]: client = genshin.GenshinClient({...}, debug=True)

In [2] user = await client.get_user(710785423)
DEBUG:genshin.client:RECORD GET https://api-os-takumi.mihoyo.com/game_record/genshin/api/index?role_id=710785423&server=os_euro
DEBUG:genshin.client:RECORD POST https://api-os-takumi.mihoyo.com/game_record/genshin/api/character
```
