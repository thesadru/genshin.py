from typing import Dict

import pytest
from genshin import MultiCookieClient


@pytest.mark.asyncio
async def test_multicookie(cookies: Dict[str, str], uid: int):
    client = MultiCookieClient()
    client.set_cookies([cookies])

    assert len(client.cookies) == 1
    assert client.cookies[0] == {m.key: m.value for m in client.session.cookie_jar}

    await client.get_user(uid)

    await client.close()
