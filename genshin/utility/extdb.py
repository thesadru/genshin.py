"""External databases for Genshin Impact data."""

import asyncio
import typing

import aiohttp

from genshin.constants import LANGS
from genshin.models.genshin import constants as model_constants

__all__ = ("update_characters_ambr", "update_characters_enka")

ENKA_CHARACTERS_URL = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/characters.json"
ENKA_LOC_URL = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json"
AMBR_URL = "https://api.ambr.top/v2/{lang}/avatar"

ELEMENTS_MAP = {
    "Fire": "Pyro",
    "Wind": "Anemo",
    "Ice": "Cryo",
    "Electric": "Electro",
    "Water": "Hydro",
    "Rock": "Geo",
    "Grass": "Dendro",
}

ENKA_LANG_MAP = {
    "zh-CN": "zh-cn",
    "zh-TW": "zh-tw",
    "de": "de-de",
    "en": "en-us",
    "es": "es-es",
    "fr": "fr-fr",
    "id": "id-id",
    "ja": "ja-jp",
    "ko": "ko-kr",
    "pt": "pt-pt",
    "ru": "ru-ru",
    "th": "th-th",
    "vi": "vi-vn",
}
ENKA_RARITY_MAP = {
    "QUALITY_PURPLE": 4,
    "QUALITY_ORANGE": 5,
    "QUALITY_PURPLE_SP": 104,
    "QUALITY_ORANGE_SP": 105,
}

AMBR_LANG_MAP = {
    "zh-cn": "chs",
    "zh-tw": "cht",
    "de-de": "de",
    "en-us": "en",
    "es-es": "es",
    "fr-fr": "fr",
    "id-id": "id",
    "ja-jp": "ja",
    "ko-kr": "ko",
    "pt-pt": "pt",
    "ru-ru": "ru",
    "th-th": "th",
    "vi-vn": "vi",
}


async def _fetch_jsons(*urls: str) -> typing.Sequence[typing.Any]:
    """Fetch multiple JSON endpoints."""
    async with aiohttp.ClientSession() as session:

        async def _fetch_and_parse(url: str) -> typing.Any:
            r = await session.get(url)
            return await r.json(content_type=None)

        return await asyncio.gather(*(_fetch_and_parse(url) for url in urls))


def update_character_name(
    lang: str,
    id: int,
    icon_name: str,
    name: str,
    element: str,
    rarity: int,
) -> None:
    """Update the character names for a specific language."""
    char = model_constants.DBChar(id, icon_name, name, element, rarity)
    model_constants.CHARACTER_NAMES.setdefault(lang, {})[id] = char


async def update_characters_enka() -> None:
    """Update characters with https://github.com/EnkaNetwork/API-docs/."""
    characters, locs = await _fetch_jsons(ENKA_CHARACTERS_URL, ENKA_LOC_URL)

    for strid, char in characters.items():
        if "-" in strid:
            continue  # traveler element

        for short_lang, loc in locs.items():
            update_character_name(
                lang=ENKA_LANG_MAP[short_lang],
                id=int(strid),
                icon_name=char["SideIconName"][len("UI_AvatarIcon_Side_") :],  # noqa: E203
                name=loc[str(char["NameTextMapHash"])],
                element=ELEMENTS_MAP[char["Element"]],
                rarity=ENKA_RARITY_MAP[char["QualityType"]],
            )


async def update_characters_ambr(langs: typing.Sequence[str] = ()) -> None:
    """Update characters with https://ambr.top/."""
    langs = langs or list(LANGS.keys())
    urls = [AMBR_URL.format(lang=AMBR_LANG_MAP[lang]) for lang in langs]

    characters_list = await _fetch_jsons(*urls)

    for lang, characters in zip(langs, characters_list):
        for strid, char in characters["data"]["items"].items():
            if "-" in strid and "anemo" not in strid:
                continue

            update_character_name(
                lang=lang,
                id=int(strid.split("-")[0]),
                icon_name=char["icon"][len("UI_AvatarIcon_") :],  # noqa: E203
                name=char["name"],
                element=ELEMENTS_MAP[char["element"]],
                rarity=char["rank"],
            )
