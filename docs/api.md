# Genshin API

For anyone wanting to make their own project which interacts with the api you may use this as a reference guide.
I will cover mainly the overseas api here.

## Game Record

Game Record, Battle Chronicle on hoyolab, refers to a collection of statistics of genshin impact players.

You may view it here: https://webstatic-sea.hoyolab.com/app/community-game-records-sea/

Internally, this page requests resources from https://api-os-takumi.mihoyo.com/game_record/genshin/api/

### Request

You are required to provide 4 headers:
```
x-rpc-language - The chosen language in iso format (english is en-us)
x-rpc-app_version - The api version you're using (currently 1.5.0)
x-rpc-client_type - The device type which requested the endpoint (desktop is 5)
ds - The dynamic secret
```

In addition to that you must provide your own user cookies. These can either be a pair of `ltuid` and `ltoken` or a pair of `account_id` and `cookie_token`.


To select a user you're requesting you must provide their uid and server.

#### Parameters

##### `role_ud`

The user's in-game uid

##### `server`

The server a player belongs to, can be figured out from the first digit in the uid
```
6XXXXXXXX = os_usa
7XXXXXXXX = os_euro
8XXXXXXXX = os_asia
9XXXXXXXX = os_cht
```


#### Dynamic secret
To generate the dynamic secret you must use the current time, a 6 character long string and a unique salt. Then generate the secret from its md5 hash. Dynamic secrets last for an hour so you should create a new one for each request.

python example:
```py
import time, hashlib

def generate_ds():
    salt = "6cqshh5dhw73bzxn20oexa9k516chk7s" # a platform-specific salt, this one is for desktop (5)
    t = int(time.time()) # the current unix time in seconds
    r = "ABCDEF" # a 6 long random string, must match [a-zA-Z0-9]

    # generate a hash from these variables and get its hex digest
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()

    # join everything together so the server can validate them
    return f"{t},{r},{h}"
```

> The ds salt had to be reverse-engineered from the hoyolab frontend source code. Your best bet is just always using this one and not worying about where it's from.

#### Example Request

curl:
```console
curl 'https://api-os-takumi.mihoyo.com/game_record/genshin/api/index?server=os_euro&role_id=710785423' \
  -H 'x-rpc-language: en-us' \
  -H 'x-rpc-app_version: 1.5.0' \
  -H 'x-rpc-client_type: 5' \
  -H 'ds: 1634484774,8BKDa5,9b54d31e1a410907605852c4c8d16e8a' \
  -H 'cookie: ltoken=cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT; ltuid=119480035'
```

python:
```py
url = 'https://api-os-takumi.mihoyo.com/game_record/genshin/api/index?server=os_euro&role_id=710785423'
headers = {
    'x-rpc-language': 'en-us',
    'x-rpc-app_version': '1.5.0',
    'x-rpc-client_type': '5',
    'ds': '1634484774,8BKDa5,9b54d31e1a410907605852c4c8d16e8a',
    'cookie': 'ltoken=cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT; ltuid=119480035',
}
response = requests.get(url, headers=headers)
```

### Response

The response is always a json object.

On success the data is returned in the data field, on failure a message and a retcode is given.

#### Example Response structure
Success:
```json
{
    "data": {<data>},
    "message": "OK",
    "retcode": 0
}
```

Failure:
```json
{
    "data": null,
    "message": "An error occured.",
    "retcode": 10000
}
```

### Endpoints

#### index

Basic user info.

```
method: GET
endpoint:  https://api-os-takumi.mihoyo.com/game_record/genshin/api/index
params: 
    server
    role_id
```
```
curl 'https://api-os-takumi.mihoyo.com/game_record/genshin/api/index?server=os_euro&role_id=710785423' \
  -H 'x-rpc-language: en-us' \
  -H 'x-rpc-app_version: 1.5.0' \
  -H 'x-rpc-client_type: 5' \
  -H 'ds: 1634484774,8BKDa5,9b54d31e1a410907605852c4c8d16e8a' \
  -H 'cookie: ltoken=cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT; ltuid=119480035'
```

#### character

Character data.

Unlike the rest of endpoints, this endpoint uses the body instead. The fields are the same as parameters with the addition of `character_ids`, that is a list of character ids that the api should return.

This request should be made after requesting the index so you can get a list of all character ids a user owns.

```
method: POST
endpoint: https://api-os-takumi.mihoyo.com/game_record/genshin/api/character
body:
    {
        "character_ids": [...],
        "role_id": ...,
        "server": ...
    }
```
```
curl 'https://api-os-takumi.mihoyo.com/game_record/genshin/api/character' \
  -H 'x-rpc-language: en-us' \
  -H 'x-rpc-app_version: 1.5.0' \
  -H 'x-rpc-client_type: 5' \
  -H 'ds: 1634484774,8BKDa5,9b54d31e1a410907605852c4c8d16e8a' \
  -H 'cookie: ltoken=cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT; ltuid=119480035'
  -d '{"character_ids":[10000026, 10000030, 10000041], "role_id":"710785423", "server":"os_euro"}'
```

#### spiralAbyss

Spiral abyss runs.

This endpoint has an additional optional param called `schedule_type`, this can either be 1 if you're requesting the current season or 2 if you're requesting the previous season.

```
method: POST
endpoint: https://api-os-takumi.mihoyo.com/game_record/genshin/api/spiralAbyss
params: 
    server
    role_id
    schedule_type
```
```
curl 'https://api-os-takumi.mihoyo.com/game_record/genshin/api/index?server=os_euro&role_id=710785423&schedule_type=2' \
  -H 'x-rpc-language: en-us' \
  -H 'x-rpc-app_version: 1.5.0' \
  -H 'x-rpc-client_type: 5' \
  -H 'ds: 1634484774,8BKDa5,9b54d31e1a410907605852c4c8d16e8a' \
  -H 'cookie: ltoken=cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT; ltuid=119480035'
```