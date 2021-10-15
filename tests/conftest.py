import asyncio
import os
import warnings
from typing import Dict, Optional

import genshin
import pytest
from genshin import ChineseClient, GenshinClient


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def cookies() -> Dict[str, str]:
    return {"ltuid": os.environ["GS_LTUID"], "ltoken": os.environ["GS_LTOKEN"]}


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
async def client(cookies: Dict[str, str]) -> GenshinClient:
    """Client with environment cookies"""
    client = GenshinClient()
    client.set_cookies(cookies)

    yield client

    await client.close()


@pytest.fixture(scope="function")
async def lclient(browser_cookies: Dict[str, str]) -> Optional[GenshinClient]:
    """The local client"""
    if not browser_cookies:
        pytest.skip("Skipped local test")
        return

    client = GenshinClient()
    client.set_cookies(browser_cookies)
    client.set_authkey()

    yield client

    await client.close()


@pytest.fixture(scope="function")
async def cnclient(chinese_cookies: Dict[str, str]) -> Optional[GenshinClient]:
    """A client with chinese cookies"""
    if not chinese_cookies:
        pytest.skip("Skipped chinese test")
        return

    client = ChineseClient()
    client.set_cookies(chinese_cookies)

    yield client

    await client.close()


@pytest.fixture(scope="session")
def uid():
    return 710785423


@pytest.fixture(scope="session")
def hoyolab_uid():
    return 8366222
