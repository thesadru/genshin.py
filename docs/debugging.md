# Debugging

## Interactive console

Since genshin.py uses asyncio it's fairly hard to debug code in the interactive console. Instead, I highly recommend you to use [IPython](https://ipython.org/).

## Requests

Genshin.py automatically logs all requests using the `logging` module. You can make these logs show up in the console by setting the `debug` kwarg to `True`

```ipython
In [1]: client = genshin.Client({...}, debug=True)

In [2]: user = await client.get_genshin_user(710785423)
DEBUG:genshin.client.components.base:GET https://webstatic-sea.mihoyo.com/admin/mi18n/bbs_cn/m11241040191111/m11241040191111-en-us.json
DEBUG:genshin.client.components.base:GET https://bbs-api-os.hoyolab.com/game_record/genshin/api/index?role_id=710785423&server=os_euro
DEBUG:genshin.client.components.base:POST https://bbs-api-os.hoyolab.com/game_record/genshin/api/character
{"role_id":710785423,"server":"os_euro"}
DEBUG:genshin.client.components.base:GET https://bbs-api-os.hoyolab.com/game_record/genshin/api/spiralAbyss?schedule_type=1&role_id=710785423&server=os_euro
DEBUG:genshin.client.components.base:GET https://bbs-api-os.hoyolab.com/game_record/genshin/api/spiralAbyss?schedule_type=2&role_id=710785423&server=os_euro
DEBUG:genshin.client.components.base:GET https://bbs-api-os.hoyolab.com/game_record/genshin/api/activities?role_id=710785423&server=os_euro
```
