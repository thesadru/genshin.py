"""Cookie completion.

Available convertions:

- update_hoyolab_cookies
    - cookie_token -> ltoken
- fetch_cookie_with_cookie
    - cookie_token -> cookie_token
    - cookie_token -> ltoken
    - stoken -> cookie_token
    - stoken -> ltoken
    - stoken -> login_ticket
- fetch_cookie_token_info
    - cookie_token -> cookie_token
    - login_ticket -> cookie_token
"""
from __future__ import annotations

import typing

import aiohttp
import aiohttp.typedefs

from genshin import errors, types
from genshin.client import routes
from genshin.client.manager import managers

__all__ = [
    "complete_cookies",
    "fetch_cookie_token_info",
    "fetch_cookie_with_cookie",
    "refresh_cookie_token",
    "update_hoyolab_cookies",
]


async def update_hoyolab_cookies(
    cookies: managers.CookieOrHeader,
    *,
    region: types.Region,
) -> typing.Mapping[str, str]:
    """Complete cookies by fetching an arbitrary endpoint."""
    cookies = managers.parse_cookie(cookies)

    base_url = routes.COMMUNITY_URL.get_url(region)
    url = base_url / "misc/wapi/langs"

    async with aiohttp.ClientSession() as session:
        r = await session.request("GET", url, cookies=cookies)
        cookies = {k: v.value for k, v in r.cookies.items()}

    return cookies


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

    cookies = await update_hoyolab_cookies(cookies, region=region)

    return cookies
