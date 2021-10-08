import asyncio
import os
from typing import Optional

import pytest

from genshin import GenshinClient
import genshin
import inspect


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
async def lclient() -> Optional[GenshinClient]:
    """The local client"""
    client = GenshinClient()
    try:
        cookies = genshin.get_browser_cookies()
    except Exception:
        cookies = {}

    if not cookies:
        yield None
        return

    client.set_cookies(cookies)
    client.set_authkey()
    asyncio.create_task(client.init())

    yield client

    await client.close()


@pytest.fixture(scope="session")
async def uid():
    return 710785423


@pytest.fixture(scope="session")
async def hoyolab_uid():
    return 8366222


@pytest.fixture(autouse=True)
def skip_local(request: pytest.FixtureRequest, lclient: GenshinClient):
    # TODO: Is there a builtin way to do this?
    sig = inspect.signature(request.function)
    fixtures = list(sig.parameters)

    if lclient is None and "lclient" in fixtures:
        pytest.skip("Skipping local test")


def pytest_configure(config):
    config.addinivalue_line("markers", "skip_local(): skip a function if working remotely")
