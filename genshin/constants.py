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
    "it-it": "Italiano",
    "ja-jp": "日本語",
    "ko-kr": "한국어",
    "pt-pt": "Português",
    "ru-ru": "Pусский",
    "th-th": "ภาษาไทย",
    "vi-vn": "Tiếng Việt",
    "tr-tr": "Türkçe",
}
"""Languages supported by the API."""

DS_SALT = {
    types.Region.OVERSEAS: "6cqshh5dhw73bzxn20oexa9k516chk7s",
    types.Region.CHINESE: "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs",
    "cn_signin": "9nQiU3AV0rJSIBWgdynfoGMGKaklfbM7",
}
"""Dynamic Secret Salts."""
