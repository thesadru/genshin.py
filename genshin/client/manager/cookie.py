"""Cookie completion.

Available convertions:

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
"""
from __future__ import annotations

import typing

import aiohttp
import aiohttp.typedefs

from genshin import errors, types, constants
from genshin.client import routes
from genshin.client.manager import managers
from genshin.utility import ds as ds_utility

__all__ = [
    "complete_cookies", 
    "refresh_cookie_token", 
    "fetch_cookie_token_info", 
    "fetch_cookie_with_cookie", 
    "fetch_cookie_with_stoken_v2",
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
    token_types: typing.List[typing.Literal[2, 4]],
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
    body = { "dst_token_types": token_types }
    
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
        else:
            raise ValueError(f"Unknown token type: {token["token_type"]}")

    return cookies


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
