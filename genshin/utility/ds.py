"""Dynamic secret generation."""
import hashlib
import json
import random
import string
import time
import typing

__all__ = [
    "generate_dynamic_secret",
    "generate_cn_dynamic_secret",
]


def generate_dynamic_secret(salt: str) -> str:
    """Create a new overseas dynamic secret."""
    t = int(time.time())
    r = "".join(random.choices(string.ascii_letters, k=6))
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()
    return f"{t},{r},{h}"


def generate_cn_dynamic_secret(
    salt: str,
    body: typing.Any = None,
    query: typing.Optional[typing.Mapping[str, typing.Any]] = None,
) -> str:
    """Create a new chinese dynamic secret."""
    t = int(time.time())
    r = random.randint(100001, 200000)
    b = json.dumps(body) if body else ""
    q = "&".join(f"{k}={v}" for k, v in sorted(query.items())) if query else ""

    h = hashlib.md5(f"salt={salt}&t={t}&r={r}&b={b}&q={q}".encode()).hexdigest()
    return f"{t},{r},{h}"
