"""Dynamic secret generation."""

import hashlib
import json
import random
import string
import time
import typing

from genshin import constants, types

__all__ = ["generate_cn_dynamic_secret", "generate_dynamic_secret", "get_ds_headers", "generate_passport_ds"]


def generate_dynamic_secret(salt: str = constants.DS_SALT[types.Region.OVERSEAS]) -> str:
    """Create a new overseas dynamic secret."""
    t = int(time.time())
    r = "".join(random.choices(string.ascii_letters, k=6))
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()
    return f"{t},{r},{h}"


def generate_cn_dynamic_secret(
    body: typing.Any = None,
    query: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    *,
    salt: str = constants.DS_SALT[types.Region.CHINESE],
) -> str:
    """Create a new chinese dynamic secret."""
    t = int(time.time())
    r = random.randint(100001, 200000)
    b = json.dumps(body) if body else ""
    q = "&".join(f"{k}={v}" for k, v in sorted(query.items())) if query else ""

    h = hashlib.md5(f"salt={salt}&t={t}&r={r}&b={b}&q={q}".encode()).hexdigest()
    return f"{t},{r},{h}"


def get_ds_headers(
    region: types.Region,
    data: typing.Any = None,
    params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    lang: typing.Optional[str] = None,
) -> typing.Dict[str, typing.Any]:
    """Get ds http headers."""
    if region == types.Region.OVERSEAS:
        ds_headers = {
            "x-rpc-app_version": "1.5.0",
            "x-rpc-client_type": "5",
            "x-rpc-language": lang,
            "ds": generate_dynamic_secret(),
        }
    elif region == types.Region.CHINESE:
        ds_headers = {
            "x-rpc-app_version": "2.11.1",
            "x-rpc-client_type": "5",
            "ds": generate_cn_dynamic_secret(data, params),
        }
    else:
        raise TypeError(f"{region!r} is not a valid region.")
    return ds_headers


_S = {
    "2.60.1": {
        "K2": "AcpNVhfh0oedCobdCyFV8EE1jMOVDy9q",
        "LK2": "1OJyMNCqFlstEQqqMOv0rKCIdTOoJhNt",
        "22": "t0qEgfub6cvueAPgR5m9aQWWVciEer7v",
        "25": "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs",
    },
    "os": "6cqshh5dhw73bzxn20oexa9k516chk7s",
    "PD": "JwYDpKvLj6MrMqqYU6jTKF17KNO2PXoS",
}


def md5(text: str):
    md5_func = hashlib.md5()
    md5_func.update(text.encode())
    return md5_func.hexdigest()


def _random_str_ds(
    salt: str,
    sets: str = string.ascii_lowercase + string.digits,
    with_body: bool = False,
    q: str = "",
    b: typing.Mapping[str, typing.Any] | None = None,
):
    i = str(int(time.time()))
    r = "".join(random.sample(sets, 6))
    s = f"salt={salt}&t={i}&r={r}"
    if with_body:
        s += f'&b={json.dumps(b) if b else ""}&q={q}'
    c = md5(s)
    return f"{i},{r},{c}"


def generate_passport_ds(q: str = "", b: typing.Mapping[str, typing.Any] | None = None):
    r = _random_str_ds(_S["PD"], string.ascii_letters, True, q, b)
    return r


# def generate_passport_ds(body: typing.Mapping[str, typing.Any]) -> str:
#     """Create a dynamic secret for Miyoushe passport API."""
#     salt = constants.DS_SALT["cn_passport"]
#     t = int(time.time())
#     r = "".join(random.sample(string.ascii_letters, 6))
#     b = json.dumps(body)
#     h = hashlib.md5(f"salt={salt}&t={t}&r={r}&b={b}&q=".encode()).hexdigest()
#     result = f"{t},{r},{h}"
#     return result
