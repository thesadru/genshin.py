import asyncio
import json
import os
import typing

import pytest

import genshin


@pytest.fixture(scope="session")
def honkai_cookies() -> typing.Mapping[str, str]:
    if not os.environ.get("HONKAI_COOKIES"):
        pytest.exit("No Honkai cookies set", 1)

    return genshin.client.manager.parse_cookie(os.environ["HONKAI_COOKIES"])


@pytest.fixture(scope="session")
def zzz_cookies() -> typing.Mapping[str, str]:
    if not os.environ.get("ZZZ_COOKIES"):
        pytest.exit("No ZZZ cookies set", 1)

    return genshin.client.manager.parse_cookie(os.environ["ZZZ_COOKIES"])


@pytest.fixture(scope="session")
def hsr_cookies() -> typing.Mapping[str, str]:
    if not os.environ.get("HSR_COOKIES"):
        pytest.exit("No HSR cookies set", 1)

    return genshin.client.manager.parse_cookie(os.environ["HSR_COOKIES"])


@pytest.fixture(scope="session")
def cookies() -> typing.Mapping[str, str]:
    if not os.environ.get("GENSHIN_COOKIES"):
        pytest.exit("No Genshin cookies set", 1)

    return genshin.client.manager.parse_cookie(os.environ["GENSHIN_COOKIES"])


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

    cookies = genshin.client.manager.parse_cookie(os.environ["CHINESE_GENSHIN_COOKIES"])

    return cookies


@pytest.fixture(scope="session")
def local_chinese_cookies() -> typing.Mapping[str, str]:
    if not os.environ.get("LOCAL_CHINESE_GENSHIN_COOKIES"):
        return {}

    cookies = genshin.client.manager.parse_cookie(os.environ["LOCAL_CHINESE_GENSHIN_COOKIES"])

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
        try:
            json.dump(cache, file, indent=4, ensure_ascii=False)
        except TypeError:
            # Some objects are not serializable
            pass


@pytest.fixture(scope="session")
def genshin_uid():
    return 832705997


@pytest.fixture(scope="session")
def honkai_uid():
    return 10001138


@pytest.fixture(scope="session")
def zzz_uid():
    return 1309335571


@pytest.fixture(scope="session")
def hsr_uid():
    return 828103396


@pytest.fixture(scope="session")
async def honkai_client(honkai_cookies: typing.Mapping[str, str], cache: genshin.Cache, honkai_uid: int):
    return genshin.Client(honkai_cookies, debug=True, game=genshin.Game.HONKAI, cache=cache, uid=honkai_uid)


@pytest.fixture(scope="session")
async def zzz_client(zzz_cookies: typing.Mapping[str, str], cache: genshin.Cache, zzz_uid: int):
    return genshin.Client(zzz_cookies, debug=True, game=genshin.Game.ZZZ, cache=cache, uid=zzz_uid)


@pytest.fixture(scope="session")
async def hsr_client(hsr_cookies: typing.Mapping[str, str], cache: genshin.Cache, hsr_uid: int):
    return genshin.Client(hsr_cookies, debug=True, game=genshin.Game.STARRAIL, cache=cache, uid=hsr_uid)


@pytest.fixture(scope="session")
async def client(cookies: typing.Mapping[str, str], cache: genshin.Cache, genshin_uid: int):
    return genshin.Client(cookies, debug=True, game=genshin.Game.GENSHIN, cache=cache, uid=genshin_uid)


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
def hoyolab_id():
    return 7368957


@pytest.fixture(scope="session")
def genshin_cnuid():
    return 101322963


@pytest.fixture(scope="session")
def miyoushe_uid():
    return 75276539


def pytest_addoption(parser: pytest.Parser):
    parser.addoption("--cooperative", action="store_true")


def pytest_collection_modifyitems(items: list[pytest.Item], config: pytest.Config):
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
