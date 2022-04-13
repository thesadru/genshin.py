"""Dynamic secret generation."""
import hashlib
import json
import random
import string
import time
import typing

from genshin import constants, types

__all__ = [
    "generate_cn_dynamic_secret",
    "generate_dynamic_secret",
]


def generate_dynamic_secret(salt: str = constants.DS_SALT[types.Region.OVERSEAS]) -> str:
    """Create a new overseas dynamic secret."""
    t = int(time.time())
    r = "".join(random.choices(string.ascii_letters, k=6))
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()
    return f"{t},{r},{h}"


def generate_cn_dynamic_secret(
    body: typing.Any = None,
    query: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    *,
    salt: str = constants.DS_SALT[types.Region.CHINESE],
) -> str:
    """Create a new chinese dynamic secret."""
    t = int(time.time())
    r = random.randint(100001, 200000)
    b = json.dumps(body) if body else ""
    q = "&".join(f"{k}={v}" for k, v in sorted(query.items())) if query else ""

    h = hashlib.md5(f"salt={salt}&t={t}&r={r}&b={b}&q={q}".encode()).hexdigest()
    return f"{t},{r},{h}"
