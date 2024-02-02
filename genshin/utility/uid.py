"""Utility functions related to genshin."""

import typing

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
]

UID_RANGE: typing.Mapping[types.Game, typing.Mapping[types.Region, typing.Sequence[int]]] = {
    types.Game.GENSHIN: {
        types.Region.OVERSEAS: (6, 7, 8, 9),
        types.Region.CHINESE: (1, 2, 5),
    },
    types.Game.STARRAIL: {
        types.Region.OVERSEAS: (6, 7, 8, 9),
        types.Region.CHINESE: (1, 2, 5),
    },
    types.Game.HONKAI: {
        types.Region.OVERSEAS: (1, 2),
        types.Region.CHINESE: (3, 4),
    },
}
"""Mapping of games and regions to their respective UID ranges."""


def create_short_lang_code(lang: str) -> str:
    """Create an alternative short lang code."""
    return lang if "zh" in lang else lang.split("-")[0]


def recognize_genshin_server(uid: int) -> str:
    """Recognize which server a Genshin UID is from."""
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

    raise ValueError(f"UID {uid} isn't associated with any server")


def get_prod_game_biz(region: types.Region, game: types.Game) -> str:
    """Get the game_biz value corresponding to a game and region."""
    game_biz = ""
    if game == types.Game.HONKAI:
        game_biz = "bh3_"
    elif game == types.Game.GENSHIN:
        game_biz = "hk4e_"
    elif game == types.Game.STARRAIL:
        game_biz = "hkrpg_"

    if region == types.Region.OVERSEAS:
        game_biz += "global"
    elif region == types.Region.CHINESE:
        game_biz += "cn"

    return game_biz


def recognize_honkai_server(uid: int) -> str:
    """Recognizes which server a Honkai UID is from."""
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
    server = {
        "1": "prod_gf_cn",
        "2": "prod_gf_cn",
        "5": "prod_qd_cn",
        "6": "prod_official_usa",
        "7": "prod_official_eur",
        "8": "prod_official_asia",
        "9": "prod_official_cht",
    }.get(str(uid)[0])

    if server:
        return server

    raise ValueError(f"UID {uid} isn't associated with any server")


def recognize_server(uid: int, game: types.Game) -> str:
    """Recognizes which server a UID is from."""
    if game == types.Game.HONKAI:
        return recognize_honkai_server(uid)
    elif game == types.Game.GENSHIN:
        return recognize_genshin_server(uid)
    elif game == types.Game.STARRAIL:
        return recognize_starrail_server(uid)
    else:
        raise ValueError(f"{game} is not a valid game")


def recognize_game(uid: int, region: types.Region) -> typing.Optional[types.Game]:
    """Recognize the game of a uid."""
    if len(str(uid)) == 8:
        return types.Game.HONKAI

    first = int(str(uid)[0])

    for game, digits in UID_RANGE.items():
        if first in digits[region]:
            return game

    return None


def recognize_region(uid: int, game: types.Game) -> typing.Optional[types.Region]:
    """Recognize the region of a uid."""
    first = int(str(uid)[0])

    for region, digits in UID_RANGE[game].items():
        if first in digits:
            return region

    return None
