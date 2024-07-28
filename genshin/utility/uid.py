"""Utility functions related to genshin."""

import typing
import warnings

from genshin import types

__all__ = [
    "create_short_lang_code",
    "get_prod_game_biz",
    "recognize_game",
    "recognize_genshin_server",
    "recognize_honkai_server",
    "recognize_region",
    "recognize_server",
    "recognize_starrail_server",
    "recognize_zzz_server",
]

UID_RANGE: typing.Mapping[types.Game, typing.Mapping[types.Region, typing.Sequence[str]]] = {
    types.Game.GENSHIN: {
        types.Region.OVERSEAS: ("6", "7", "8", "18", "9"),
        types.Region.CHINESE: ("1", "2", "3", "5"),
    },
    types.Game.STARRAIL: {
        types.Region.OVERSEAS: ("6", "7", "8", "9"),
        types.Region.CHINESE: ("1", "2", "5"),
    },
    types.Game.HONKAI: {
        types.Region.OVERSEAS: ("1", "2"),
        types.Region.CHINESE: ("3", "4"),
    },
}
"""Mapping of games and regions to their respective UID ranges."""

GENSHIN_SERVER_RANGE: typing.Mapping[str, typing.Sequence[str]] = {
    "cn_gf01": ("1", "2", "3"),
    "cn_qd01": ("5",),
    "os_usa": ("6",),
    "os_euro": ("7",),
    "os_asia": ("8", "18"),
    "os_cht": ("9",),
}
"""Mapping of Genshin servers to their respective UID ranges."""

STARRAIL_SERVER_RANGE: typing.Mapping[str, typing.Sequence[str]] = {
    "prod_gf_cn": ("1", "2"),
    "prod_qd_cn": ("5",),
    "prod_official_usa": ("6",),
    "prod_official_eur": ("7",),
    "prod_official_asia": ("8",),
    "prod_official_cht": ("9",),
}
"""Mapping of Star Rail servers to their respective UID ranges."""

ZZZ_SERVER_RANGE: typing.Mapping[str, typing.Sequence[str]] = {
    "prod_gf_us": ("10",),
    "prod_gf_eu": ("15",),
    "prod_gf_jp": ("13",),
    "prod_gf_sg": ("17",),
}
"""Mapping of global Zenless Zone Zero servers to their respective UID ranges."""


def create_short_lang_code(lang: str) -> str:
    """Create an alternative short lang code."""
    return lang if "zh" in lang else lang.split("-")[0]


def recognize_genshin_server(uid: int) -> str:
    """Recognize which server a Genshin UID is from."""
    for server_name, digits in GENSHIN_SERVER_RANGE.items():
        if str(uid)[:-8] in digits:
            return server_name

    raise ValueError(f"UID {uid} isn't associated with any server")


def get_prod_game_biz(region: types.Region, game: types.Game) -> str:
    """Get the game_biz value corresponding to a game and region."""
    game_biz = ""
    if game is types.Game.HONKAI:
        game_biz = "bh3_"
    elif game is types.Game.GENSHIN:
        game_biz = "hk4e_"
    elif game is types.Game.STARRAIL:
        game_biz = "hkrpg_"
    elif game is types.Game.ZZZ:
        game_biz = "nap_"
    elif game is types.Game.TOT:
        game_biz = "nxx_"

    if region is types.Region.OVERSEAS:
        game_biz += "global"
    elif region is types.Region.CHINESE:
        game_biz += "cn"

    return game_biz


def recognize_honkai_server(uid: int) -> str:
    """Recognizes which server a Honkai UID is from."""
    warnings.warn("recognize_honkai_server is unreliable, avoid using it.")
    if 10000000 < uid < 100000000:
        return "overseas01"
    elif 100000000 < uid < 200000000:
        return "usa01"
    elif 200000000 < uid < 300000000:
        return "eur01"

    # From what I can tell, CN UIDs are all over the place,
    # seemingly even overlapping with overseas UIDs...
    # Probably gonna need some input from actual CN players here, but I know none.
    # It could be that e.g. global range is 2e8 ~ 2.5e8
    raise ValueError(f"UID {uid} isn't associated with any server")


def recognize_starrail_server(uid: int) -> str:
    """Recognize which server a Star Rail UID is from."""
    for server, digits in STARRAIL_SERVER_RANGE.items():
        if str(uid)[:-8] in digits:
            return server

    raise ValueError(f"UID {uid} isn't associated with any server")


def recognize_zzz_server(uid: int) -> str:
    """Recognize which server a Zenless Zone Zero UID is from."""
    # CN region UIDs only has 8 digits, global has 10, so we use this method to recognize the server
    # This might change in the future when UIDs run out but... let's keep it like this for now
    if len(str(uid)) == 8:
        return "prod_gf_cn"

    for server, digits in ZZZ_SERVER_RANGE.items():
        if str(uid)[:-8] in digits:
            return server

    raise ValueError(f"UID {uid} isn't associated with any server")


def recognize_server(uid: int, game: types.Game) -> str:
    """Recognizes which server a UID is from."""
    if game is types.Game.GENSHIN:
        return recognize_genshin_server(uid)
    if game is types.Game.STARRAIL:
        return recognize_starrail_server(uid)
    if game is types.Game.ZZZ:
        return recognize_zzz_server(uid)

    raise ValueError(f"recognize_server is not implemented for game {game}")


def recognize_game(uid: int, region: types.Region) -> typing.Optional[types.Game]:
    """Recognize the game of a uid."""
    if len(str(uid)) == 8:
        return types.Game.HONKAI

    for game, digits in UID_RANGE.items():
        if str(uid)[:-8] in digits[region]:
            return game

    return None


def recognize_region(uid: int, game: types.Game) -> typing.Optional[types.Region]:
    """Recognize the region of a uid."""
    if game in {types.Game.ZZZ, types.Game.TOT}:
        if len(str(uid)) == 8:
            return types.Region.CHINESE
        return types.Region.OVERSEAS

    if game not in UID_RANGE:
        return None

    for region, digits in UID_RANGE[game].items():
        if str(uid)[:-8] in digits:
            return region

    return None
