import asyncio
import json
import os
import typing
import warnings

import pytest

import genshin


@pytest.fixture(scope="session")
def event_loop():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        loop = asyncio.get_event_loop()

    yield loop
    loop.close()


@pytest.fixture(scope="session")
def cookies() -> typing.Mapping[str, str]:
    if not os.environ.get("GENSHIN_COOKIES"):
        pytest.exit("No cookies set", 1)

    cookies = genshin.client.manager.parse_cookie(os.environ["GENSHIN_COOKIES"])

    return cookies


@pytest.fixture(scope="session")
def local_cookies() -> typing.Mapping[str, str]:
    try:
        cookies = genshin.utility.get_browser_cookies()
    except Exception:
        cookies = {}

    if not cookies:
        if not os.environ.get("LOCAL_GENSHIN_COOKIES"):
            return {}

        cookies = genshin.client.manager.parse_cookie(os.environ["LOCAL_GENSHIN_COOKIES"])

    return cookies


@pytest.fixture(scope="session")
def chinese_cookies() -> typing.Mapping[str, str]:
    if not os.environ.get("CHINESE_GENSHIN_COOKIES"):
        return {}

    cookies = genshin.client.manager.parse_cookie(os.environ["GENSHIN_COOKIES"])

    return cookies


@pytest.fixture(scope="session")
def local_chinese_cookies() -> typing.Mapping[str, str]:
    if not os.environ.get("LOCAL_CHINESE_GENSHIN_COOKIES"):
        return {}

    cookies = genshin.client.manager.parse_cookie(os.environ["LOCAL_GENSHIN_COOKIES"])

    return cookies


@pytest.fixture(scope="session")
async def cache():
    """Return a session that gets its contents dumped into a log file."""
    cache = genshin.Cache()
    yield cache

    cache = {str(key): value for key, (_, value) in cache.cache.items()}

    cache["CHARACTER_NAMES"] = {
        lang: [c._asdict() for c in chars.values()] for lang, chars in genshin.models.CHARACTER_NAMES.items()
    }
    cache["BATTLESUIT_IDENTIFIERS"] = genshin.models.BATTLESUIT_IDENTIFIERS

    os.makedirs(".pytest_cache", exist_ok=True)
    with open(".pytest_cache/hoyo_cache.json", "w", encoding="utf-8") as file:
        json.dump(cache, file, indent=4, ensure_ascii=False)


@pytest.fixture(scope="session")
async def client(cookies: typing.Mapping[str, str], cache: genshin.Cache):
    """Return a client with environment cookies."""
    client = genshin.Client()
    client.debug = True
    client.set_cookies(cookies)
    client.cache = cache

    return client


@pytest.fixture(scope="session")
async def lclient(local_cookies: typing.Mapping[str, str], cache: genshin.Cache):
    """Return the local client."""
    if not local_cookies:
        pytest.skip("Skipped local test")

    client = genshin.Client()
    client.debug = True
    client.default_game = genshin.Game.GENSHIN
    client.set_cookies(local_cookies)
    try:
        client.set_authkey()
    except (FileNotFoundError, ValueError):
        pass

    client.cache = cache

    return client


@pytest.fixture(scope="session")
async def authkey(lclient: genshin.GenshinClient):
    if lclient.authkey is None:
        pytest.skip("Skipped authkey test")

    try:
        await lclient.wish_history(200, limit=1)
    except genshin.AuthkeyException as e:
        pytest.skip(f"Skipped authkey test ({e.msg})")

    return lclient.authkey


@pytest.fixture(scope="session")
async def cnclient(chinese_cookies: typing.Mapping[str, str]):
    """Return the client with chinese cookies."""
    if not chinese_cookies:
        pytest.skip("Skipped chinese test")

    client = genshin.Client()
    client.region = genshin.types.Region.CHINESE
    client.debug = True
    client.set_cookies(chinese_cookies)

    return client


@pytest.fixture(scope="session")
async def lcnclient(local_chinese_cookies: typing.Mapping[str, str]):
    """Return the local client with chinese cookies."""
    if not local_chinese_cookies:
        pytest.skip("Skipped local chinese test")
        return

    client = genshin.Client()
    client.region = genshin.types.Region.CHINESE
    client.debug = True
    client.set_cookies(local_chinese_cookies)

    return client


@pytest.fixture(scope="session")
def genshin_uid():
    return 710785423


@pytest.fixture(scope="session")
def honkai_uid():
    return 200365120


@pytest.fixture(scope="session")
def hoyolab_uid():
    return 8366222


@pytest.fixture(scope="session")
def genshin_cnuid():
    return 101322963


@pytest.fixture(scope="session")
def miyoushe_uid():
    return 75276539


def pytest_addoption(parser: pytest.Parser):
    parser.addoption("--cooperative", action="store_true")


def pytest_collection_modifyitems(items: typing.List[pytest.Item], config: pytest.Config):
    if config.option.cooperative:
        for item in items:
            if isinstance(item, pytest.Function) and asyncio.iscoroutinefunction(item.obj):
                item.add_marker("asyncio_cooperative")

    for index, item in enumerate(items):
        if "reserialization" in item.name:
            break
    else:
        return items

    item = items.pop(index)
    items.append(item)

    return items
