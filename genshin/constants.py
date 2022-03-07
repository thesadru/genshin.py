"""Constants hardcoded for optimizations."""
from . import types

__all__ = ["LANGS"]


LANGS = {
    "zh-cn": "简体中文",
    "zh-tw": "繁體中文",
    "de-de": "Deutsch",
    "en-us": "English",
    "es-es": "Español",
    "fr-fr": "Français",
    "id-id": "Indonesia",
    "ja-jp": "日本語",
    "ko-kr": "한국어",
    "pt-pt": "Português",
    "ru-ru": "Pусский",
    "th-th": "ภาษาไทย",
    "vi-vn": "Tiếng Việt",
}
"""Languages supported by the API."""

DS_SALT = {
    types.Region.OVERSEAS: "6cqshh5dhw73bzxn20oexa9k516chk7s",
    types.Region.CHINESE: "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs",
}

ACT_ID = {
    types.Region.OVERSEAS: "e202102251931481",
    types.Region.CHINESE: "e202009291139501",
}
