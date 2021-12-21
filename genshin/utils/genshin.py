"""Utility functions related to genshin fuckery"""
import hashlib
import json
import random
import re
import string
import time
from typing import Any, Mapping, Union

__all__ = [
    "generate_dynamic_secret",
    "generate_cn_dynamic_secret",
    "create_short_lang_code",
    "recognize_server",
    "recognize_id",
    "is_genshin_uid",
    "is_chinese",
]


def generate_dynamic_secret(salt: str) -> str:
    """Creates a new overseas dynamic secret

    :param salt: A ds salt
    """
    t = int(time.time())
    r = "".join(random.choices(string.ascii_letters, k=6))
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()
    return f"{t},{r},{h}"


def generate_cn_dynamic_secret(salt: str, body: Any = None, query: Mapping[str, Any] = None) -> str:
    """Creates a new chinese dynamic secret

    :param salt: A ds salt
    :param body: A json body of the request
    :param query: A query of the request
    """
    t = int(time.time())
    r = random.randint(100001, 200000)
    b = json.dumps(body) if body else ""
    q = "&".join(f"{k}={v}" for k, v in sorted(query.items())) if query else ""

    h = hashlib.md5(f"salt={salt}&t={t}&r={r}&b={b}&q={q}".encode()).hexdigest()
    return f"{t},{r},{h}"


def create_short_lang_code(lang: str) -> str:
    """Returns an alternative short lang code

    :param lang: A language code
    """
    return lang if "zh" in lang else lang.split("-")[0]


def recognize_server(uid: int) -> str:
    """Recognizes which server a UID is from.

    :param uid: A genshin uid
    """
    server = {
        "1": "cn_gf01",
        "2": "cn_gf01",
        "5": "cn_qd01",
        "6": "os_usa",
        "7": "os_euro",
        "8": "os_asia",
        "9": "os_cht",
    }.get(str(uid)[0])

    if server:
        return server
    else:
        raise ValueError(f"UID {uid} isn't associated with any server")


def recognize_id(id: int):
    """Attempts to recognize what item type an id is

    :param id: Any id
    :returns: A model for the appropriate id
    """
    from .. import models

    if 10000000 < id < 20000000:
        return models.genshin.BaseCharacter
    elif 1000000 < id < 10000000:
        return models.genshin.character.ArtifactSet
    elif 100000 < id < 1000000:
        return models.genshin.character.Outfit
    elif 50000 < id < 100000:
        return models.genshin.character.Artifact
    elif 10000 < id < 50000:
        return models.genshin.character.Weapon
    elif 100 < id < 1000:
        return models.genshin.character.Constellation
    elif 10e17 < id < 10e19:
        return models.genshin.wish.Wish
    else:
        return None


def is_genshin_uid(uid: int) -> bool:
    """Recognizes whether the uid is a valid genshin uid

    Doesn't work for chinese uids.

    :param uid: A genshin or hoyolab uid
    """
    return bool(re.fullmatch(r"[6789]\d{8}", str(uid)))


def is_chinese(x: Union[int, str]) -> bool:
    """Recognizes whether the server/uid is chinese

    :param x: A server or a genshin uid
    """
    return str(x).startswith(("cn", "1", "2", "5"))
