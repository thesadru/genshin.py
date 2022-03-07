"""Utility functions related to genshin."""
import typing

__all__ = [
    "create_short_lang_code",
    "recognize_genshin_server",
    "is_chinese",
]


def create_short_lang_code(lang: str) -> str:
    """Create an alternative short lang code."""
    return lang if "zh" in lang else lang.split("-")[0]


def recognize_genshin_server(uid: int) -> str:
    """Recognize which server a UID is from."""
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


def is_chinese(x: typing.Union[int, str]) -> bool:
    """Recognize whether the server/uid is chinese."""
    return str(x).startswith(("cn", "1", "2", "5"))
