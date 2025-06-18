"""Cookie completion.

Available conversions:

- fetch_cookie_with_cookie
    - cookie_token -> cookie_token
    - cookie_token -> ltoken
    - stoken -> cookie_token
    - stoken -> ltoken
    - stoken -> login_ticket
- fetch_cookie_token_info
    - cookie_token -> cookie_token
    - login_ticket -> cookie_token
- fetch_cookie_with_stoken_v2
    - stoken (v2) + mid -> ltoken_v2 (token_type=2)
    - stoken (v2) + mid -> cookie_token_v2 (token_type=4)
- cn_fetch_cookie_token_with_stoken_v2
    - stoken (v2) + mid -> cookie_token
- fetch_cookie_token_with_game_token
    - game_token -> cookie_token
- fetch_stoken_with_game_token
    - game_token -> stoken
"""

from __future__ import annotations

import random
import typing
import uuid
from string import ascii_letters, digits

import aiohttp

from genshin import constants, errors, types
from genshin.client import routes
from genshin.client.manager import managers
from genshin.models.auth.cookie import StokenResult
from genshin.utility import ds as ds_utility

__all__ = [
    "cn_fetch_cookie_token_with_stoken_v2",
    "complete_cookies",
    "fetch_cookie_token_info",
    "fetch_cookie_token_with_game_token",
    "fetch_cookie_with_cookie",
    "fetch_cookie_with_stoken_v2",
    "fetch_stoken_with_game_token",
    "refresh_cookie_token",
]


async def fetch_cookie_with_cookie(
    cookies: managers.CookieOrHeader,
    *,
    source: typing.Literal["CookieToken", "SToken"],
    target: typing.Literal["CookieAccountInfo", "LToken", "ActionTicket"],
    region: types.Region = types.Region.OVERSEAS,
) -> typing.Mapping[str, str]:
    """Fetch cookie token info with an stoken."""
    cookies = managers.parse_cookie(cookies)

    base_url = routes.ACCOUNT_URL.get_url(region)
    url = base_url / f"get{target}By{source}"

    body = cookies.copy()
    account_id = body.pop("ltuid", None) or body.pop("account_id")
    body["uid"] = account_id
    if target == "ActionTicket":
        body["action_type"] = "login"

    async with aiohttp.ClientSession() as session:
        r = await session.request("POST", url, json=body)
        data = await r.json(content_type=None)

    if data["retcode"] != 0:
        errors.raise_for_retcode(data)

    cookies = dict(data["data"])
    if account_id := cookies.pop("uid"):
        cookies["account_id"] = account_id

    return data


async def fetch_cookie_with_stoken_v2(
    cookies: managers.CookieOrHeader,
    *,
    token_types: list[typing.Literal[2, 4]],
) -> typing.Mapping[str, str]:
    """Fetch cookie (v2) with an stoken (v2) and mid."""
    cookies = managers.parse_cookie(cookies)
    if "ltmid_v2" in cookies:
        # The endpoint requires ltmid_v2 to be named mid
        cookies["mid"] = cookies["ltmid_v2"]

    url = routes.COOKIE_V2_REFRESH_URL.get_url()

    headers = {
        "ds": ds_utility.generate_dynamic_secret(constants.DS_SALT["app_login"]),
        "x-rpc-app_id": "c9oqaq3s3gu8",
    }
    body = {"dst_token_types": token_types}

    async with aiohttp.ClientSession() as session:
        r = await session.request("POST", url, json=body, headers=headers, cookies=cookies)
        data = await r.json(content_type=None)

    if data["retcode"] != 0:
        errors.raise_for_retcode(data)

    cookies = dict()
    for token in data["data"]["tokens"]:
        if token["token_type"] == 2:
            cookies["ltoken_v2"] = token["token"]
        elif token["token_type"] == 4:
            cookies["cookie_token_v2"] = token["token"]

    return cookies


async def cn_fetch_cookie_token_with_stoken_v2(
    cookies: managers.CookieOrHeader,
) -> typing.Mapping[typing.Literal["uid", "cookie_token"], str]:
    """Fetch cookie_token with an stoken (v2) and mid."""
    cookies = managers.parse_cookie(cookies)
    url = routes.CN_GET_COOKIE_TOKEN_BY_STOKEN_URL.get_url()

    headers = {
        "ds": ds_utility.generate_dynamic_secret(constants.DS_SALT["app_login"]),
        "x-rpc-app_id": "bll8iq97cem8",
    }
    async with aiohttp.ClientSession() as session:
        r = await session.request("GET", url, headers=headers, cookies=cookies)
        data = await r.json()

    if data["retcode"] != 0:
        errors.raise_for_retcode(data)

    return data["data"]


async def fetch_cookie_token_info(
    cookies: managers.CookieOrHeader,
    *,
    source: typing.Literal["cookie_token", "login_ticket"],
    region: types.Region = types.Region.OVERSEAS,
) -> typing.Mapping[str, typing.Any]:
    """Fetch cookie token info."""
    cookies = managers.parse_cookie(cookies)

    base_url = routes.WEBAPI_URL.get_url(region)
    if source == "cookie_token":
        url = base_url / "fetch_cookie_accountinfo"
    elif source == "login_ticket":
        url = base_url / "cookie_accountinfo_by_loginticket"
    else:
        raise ValueError("Invalid source")

    async with aiohttp.ClientSession() as session:
        r = await session.request("GET", url, cookies=cookies)
        data = await r.json()

    data = data["data"]
    if data["status"] != 1 or not data or not data["cookie_info"]:
        raise errors.CookieException(msg=f"Error fetching cookie token info {data['status']}")

    return data["cookie_info"]


async def refresh_cookie_token(
    cookies: managers.CookieOrHeader,
    *,
    source: typing.Literal["cookie_token", "login_ticket"] = "cookie_token",
    region: types.Region = types.Region.OVERSEAS,
) -> typing.MutableMapping[str, str]:
    """Refresh a cookie token to make it last longer."""
    cookies = managers.parse_cookie(cookies)

    info = await fetch_cookie_token_info(cookies, region=region, source=source)
    cookies["account_id"] = info["account_id"]
    cookies["cookie_token"] = info["cookie_token"]

    return cookies


async def complete_cookies(
    cookies: managers.CookieOrHeader,
    *,
    refresh: bool = True,
    region: types.Region = types.Region.OVERSEAS,
) -> typing.Mapping[str, str]:
    """Add ltoken and ltuid to a cookie with only a cookie_token and an account_id.

    If refresh is True, the cookie token will be refreshed to last longer.
    """
    cookies = managers.parse_cookie(cookies)

    if refresh:
        cookies = await refresh_cookie_token(cookies, region=region)  # type: ignore[assignment]

    return cookies


async def fetch_cookie_token_with_game_token(*, game_token: str, account_id: str) -> str:
    """Fetch cookie token with game token, which can be obtained by scanning a QR code."""
    url = routes.GET_COOKIE_TOKEN_BY_GAME_TOKEN_URL.get_url()
    params = {
        "game_token": game_token,
        "account_id": account_id,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as r:
            data = await r.json()

    if not data["data"]:
        errors.raise_for_retcode(data)

    return data["data"]["cookie_token"]


async def fetch_stoken_with_game_token(*, game_token: str, account_id: int) -> StokenResult:
    """Fetch cookie token with game token, which can be obtained by scanning a QR code."""
    url = routes.GET_STOKEN_BY_GAME_TOKEN_URL.get_url()
    payload = {
        "account_id": account_id,
        "game_token": game_token,
    }
    headers = {
        "DS": ds_utility.generate_passport_ds(body=payload),
        "x-rpc-device_id": uuid.uuid4().hex,
        "x-rpc-device_fp": "".join(random.choices(ascii_letters + digits, k=13)),
        "x-rpc-app_id": "bll8iq97cem8",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as r:
            data = await r.json()

    if not data["data"]:
        errors.raise_for_retcode(data)

    return StokenResult(**data["data"])
