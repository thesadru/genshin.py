import pytest
from genshin import MultiCookieClient, GenshinClient


@pytest.mark.asyncio_cooperative
async def test_multicookie(client: GenshinClient, uid: int):
    cookies = client.cookies

    client = MultiCookieClient()
    client.set_cookies([cookies])

    assert len(client.cookies) == 1
    assert client.cookies[0] == {m.key: m.value for m in client.session.cookie_jar}

    await client.get_user(uid)

    await client.close()
