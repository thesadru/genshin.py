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
    types.Region.OVERSEAS: "6s25p5ox5y14umn1p61aqyyvbvvl3lrt",
    types.Region.CHINESE: "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs",
    "app_login": "IZPgfb0dRPtBeLuFkdDznSZ6f4wWt6y2",
    "cn_signin": "9nQiU3AV0rJSIBWgdynfoGMGKaklfbM7",
    "cn_passport": "JwYDpKvLj6MrMqqYU6jTKF17KNO2PXoS",
}
"""Dynamic Secret Salts."""

MIYOUSHE_GEETEST_RETCODES = {10035, 5003, 10041, 1034}
"""API error codes that indicate a Geetest was triggered during this Miyoushe API request."""

APP_KEYS = {
    types.Game.GENSHIN: {
        types.Region.OVERSEAS: "6a4c78fe0356ba4673b8071127b28123",
        types.Region.CHINESE: "d0d3a7342df2026a70f650b907800111",
    },
    types.Game.STARRAIL: {
        types.Region.OVERSEAS: "d74818dabd4182d4fbac7f8df1622648",
        types.Region.CHINESE: "4650f3a396d34d576c3d65df26415394",
    },
}
