# Debugging

## Interactive console

Since genshin.py uses asyncio it's fairly hard to debug code in the interactive console. Instead I highly recommend you use [IPython](https://ipython.org/).

## Requests

Genshin.py automatically logs all requests using the `logging` module. You can make these logs show up in the console by setting the `debug` kwarg to `True`

```ipython
In [1]: client = genshin.GenshinClient({...}, debug=True)

In [2]: user = await client.get_user(710785423)
DEBUG:genshin.client:GET https://bbs-api-os.mihoyo.com/game_record/genshin/api/index?server=os_euro&role_id=710785423
DEBUG:genshin.client:POST https://bbs-api-os.mihoyo.com/game_record/genshin/api/character
{"character_ids":[10000003,10000006,10000007,10000014,10000015,10000020,10000021,10000023,10000024,10000025],"role_id":710785423,"server":"os_euro"}
```
