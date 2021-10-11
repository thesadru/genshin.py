import asyncio
import os
from typing import Dict, Optional

import pytest

from genshin import GenshinClient
import genshin


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client() -> GenshinClient:
    """Client with environment cookies"""
    client = GenshinClient()

    cookies = {"ltuid": os.environ["GS_LTUID"], "ltoken": os.environ["GS_LTOKEN"]}
    client.set_cookies(cookies)

    yield client

    await client.close()


@pytest.fixture(scope="session")
def browser_cookies() -> Dict[str, str]:
    try:
        return genshin.get_browser_cookies()
    except Exception:
        return {}


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


@pytest.fixture(scope="session")
def uid():
    return 710785423


@pytest.fixture(scope="session")
def hoyolab_uid():
    return 8366222
