import asyncio
import json
import os
import warnings
from typing import Dict

import pytest

import genshin
from genshin import ChineseClient, GenshinClient


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def cookies() -> Dict[str, str]:
    try:
        return {"ltuid": os.environ["LTUID"], "ltoken": os.environ["LTOKEN"]}
    except KeyError:
        pytest.exit("No cookies set", 1)
        return {}


@pytest.fixture(scope="session")
def browser_cookies() -> Dict[str, str]:
    try:
        return genshin.get_browser_cookies()
    except Exception:
        return {}


@pytest.fixture(scope="session")
def chinese_cookies() -> Dict[str, str]:
    try:
        return {"ltuid": os.environ["CN_LTUID"], "ltoken": os.environ["CN_LTOKEN"]}
    except KeyError:
        warnings.warn("No chinese cookies were set for tests")
        return {}


@pytest.fixture(scope="session")
def local_chinese_cookies() -> Dict[str, str]:
    try:
        return {
            "account_id": os.environ["LCN_ACCOUNT_ID"],
            "cookie_token": os.environ["LCN_COOKIE_TOKEN"],
        }
    except KeyError:
        return {}


@pytest.fixture(scope="session")
async def client(cookies: Dict[str, str]):
    """Client with environment cookies"""
    client = GenshinClient()
    client.debug = True
    client.set_cookies(cookies)
    client.cache = {}

    yield client

    await client.close()

    # dump the entire cache into a json file
    cache = {}
    parsed = {}
    for k, v in client.cache.items():
        key = "|".join(map(str, k))
        cache[key] = v
        if k[0] == "user":
            parsed[key] = json.loads(genshin.models.PartialUserStats(**v).json())
        elif k[0] == "characters":
            parsed[key] = [json.loads(genshin.models.Character(**i).json()) for i in v["avatars"]]
        elif k[0] == "abyss":
            parsed[key] = json.loads(genshin.models.SpiralAbyss(**v).json())
        elif k[0] == "record":
            parsed[key] = json.loads(genshin.models.RecordCard(**v["list"][0]).json())
        elif k[0] == "activities":
            parsed[key] = json.loads(genshin.models.Activities(**v).json())

    os.makedirs(".pytest_cache", exist_ok=True)
    with open(".pytest_cache/genshin_cache.json", "w") as file:
        json.dump(cache, file, indent=4)
    with open(".pytest_cache/parsed_genshin_cache.json", "w") as file:
        json.dump(parsed, file, indent=4)


@pytest.fixture(scope="session")
async def lclient(browser_cookies: Dict[str, str]):
    """The local client"""
    if not browser_cookies:
        pytest.skip("Skipped local test")
        return

    client = GenshinClient()
    client.debug = True
    client.set_cookies(browser_cookies)
    client.set_authkey()

    yield client

    await client.close()


@pytest.fixture(scope="session")
async def cnclient(chinese_cookies: Dict[str, str]):
    """A client with chinese cookies"""
    if not chinese_cookies:
        pytest.skip("Skipped chinese test")
        return

    client = ChineseClient()
    client.debug = True
    client.set_cookies(chinese_cookies)

    yield client

    await client.close()


@pytest.fixture(scope="session")
async def lcnclient(local_chinese_cookies: Dict[str, str]):
    """A local client with chinese cookies"""
    if not local_chinese_cookies:
        pytest.skip("Skipped local chinese test")
        return

    client = ChineseClient()
    client.debug = True
    client.set_cookies(local_chinese_cookies)

    yield client

    await client.close()


@pytest.fixture(scope="session")
def uid():
    return 710785423


@pytest.fixture(scope="session")
def hoyolab_uid():
    return 8366222


@pytest.fixture(scope="session")
def cnuid():
    return 101322963


@pytest.fixture(scope="session")
def miyoushe_uid():
    return 75276539
