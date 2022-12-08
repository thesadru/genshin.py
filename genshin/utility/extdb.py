"""External databases for Genshin Impact data."""

import asyncio
import json
import time
import typing
import warnings

import aiohttp

from genshin.constants import LANGS
from genshin.models.genshin import constants as model_constants
from genshin.utility import fs

__all__ = ("update_characters_ambr", "update_characters_enka", "update_characters_genshindata")

CACHE_FILE = fs.get_tempdir() / "characters.json"

if CACHE_FILE.exists() and time.time() - CACHE_FILE.stat().st_mtime < 7 * 24 * 60 * 60:
    names = json.loads(CACHE_FILE.read_text())
    try:
        model_constants.CHARACTER_NAMES = {
            lang: {int(char_id): model_constants.DBChar(*char) for char_id, char in chars.items()}
            for lang, chars in names.items()
        }
    except Exception:
        warnings.warn("Failed to load character names from cache")
        CACHE_FILE.unlink()

GENSHINDATA_CHARACTERS_URL = "https://raw.githubusercontent.com/Dimbreath/GenshinData/master/ExcelBinOutput/AvatarExcelConfigData.json"  # fmt: off  # noqa
GENSHINDATA_TALENT_DEPOT_URL = "https://raw.githubusercontent.com/Dimbreath/GenshinData/master/ExcelBinOutput/AvatarSkillDepotExcelConfigData.json"  # fmt: off  # noqa
GENSHINDATA_TALENT_URL = "https://raw.githubusercontent.com/Dimbreath/GenshinData/master/ExcelBinOutput/AvatarSkillExcelConfigData.json"  # fmt: off  # noqa
GENSHINDATA_TEXTMAP_URL = "https://raw.githubusercontent.com/Dimbreath/GenshinData/master/TextMap/TextMap{lang}.json"
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
RARITY_MAP = {
    "QUALITY_PURPLE": 4,
    "QUALITY_ORANGE": 5,
    "QUALITY_PURPLE_SP": 104,
    "QUALITY_ORANGE_SP": 105,
}
LANG_MAP = {
    "zh-cn": "chs",
    "zh-tw": "cht",
    "de-de": "de",
    "en-us": "en",
    "es-es": "es",
    "fr-fr": "fr",
    "id-id": "id",
    "it-it": "it",
    "ja-jp": "jp",
    "ko-kr": "kr",
    "pt-pt": "pt",
    "ru-ru": "ru",
    "th-th": "th",
    "vi-vn": "vi",
    "tr-tr": "tr",
}
ENKA_LANG_MAP = {
    "zh-CN": "zh-cn",
    "zh-TW": "zh-tw",
    "de": "de-de",
    "en": "en-us",
    "es": "es-es",
    "fr": "fr-fr",
    "id": "id-id",
    "it": "it-it",
    "ja": "ja-jp",
    "ko": "ko-kr",
    "pt": "pt-pt",
    "ru": "ru-ru",
    "th": "th-th",
    "vi": "vi-vn",
    "tr": "tr",
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


async def update_characters_genshindata(langs: typing.Sequence[str] = ()) -> None:
    """Update characters with https://github.com/Dimbreath/GenshinData/.

    This method requires the download of >20MB per language so it's not recommended.
    """
    langs = langs or list(LANGS.keys())
    urls = [GENSHINDATA_TEXTMAP_URL.format(lang=LANG_MAP[lang].upper()) for lang in langs]

    # I love spamming github
    characters, talent_depot, talents, *textmaps = await _fetch_jsons(
        GENSHINDATA_CHARACTERS_URL,
        GENSHINDATA_TALENT_DEPOT_URL,
        GENSHINDATA_TALENT_URL,
        *urls,
    )

    talent_depot = {talent["id"]: talent for talent in talent_depot}
    talents = {talent["id"]: talent for talent in talents}

    for char in characters:
        for lang, textmap in zip(langs, textmaps):
            if char["skillDepotId"] == 101 or char["iconName"].endswith("_Kate") or str(char["id"])[:2] == "11":
                continue  # test character

            if char["candSkillDepotIds"]:
                raw_element = "Wind"  # traveler
            else:
                talent = talent_depot[char["skillDepotId"]]
                raw_element = talents[talent["energySkill"]]["costElemType"]

            update_character_name(
                lang=lang,
                id=char["id"],
                icon_name=char["iconName"][len("UI_AvatarIcon_") :],  # noqa: E203
                name=textmap[str(char["nameTextMapHash"])],
                element=ELEMENTS_MAP[raw_element],
                rarity=RARITY_MAP[char["qualityType"]],
            )

    CACHE_FILE.write_text(json.dumps(model_constants.CHARACTER_NAMES))


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
                rarity=RARITY_MAP[char["QualityType"]],
            )

    CACHE_FILE.write_text(json.dumps(model_constants.CHARACTER_NAMES))


async def update_characters_ambr(langs: typing.Sequence[str] = ()) -> None:
    """Update characters with https://ambr.top/."""
    langs = langs or list(LANGS.keys())
    urls = [AMBR_URL.format(lang=LANG_MAP[lang]) for lang in langs]

    characters_list = await _fetch_jsons(*urls)

    for lang, characters in zip(langs, characters_list):
        for strid, char in characters["data"]["items"].items():
            if "-" in strid and "anemo" not in strid:
                continue  # traveler element

            update_character_name(
                lang=lang,
                id=int(strid.split("-")[0]),
                icon_name=char["icon"][len("UI_AvatarIcon_") :],  # noqa: E203
                name=char["name"],
                element=ELEMENTS_MAP[char["element"]],
                rarity=char["rank"],
            )

    CACHE_FILE.write_text(json.dumps(model_constants.CHARACTER_NAMES))
