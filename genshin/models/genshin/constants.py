"""Genshin model constants."""

import typing

__all__ = ["CHARACTER_NAMES", "DBChar"]


class DBChar(typing.NamedTuple):
    """Partial genshin character data."""

    id: int
    icon_name: str  # standardized icon name
    name: str  # localized name
    element: str
    rarity: int

    guessed: bool = False


# _RAW_DB_CHAR = typing.Union[typing.Tuple[str, str, str, int], typing.Tuple[str, str, int]]
# _character_names: typing.Mapping[int, typing.Optional[_RAW_DB_CHAR]] = {
#     10000001: None,
#     10000002: ("Ayaka", "Kamisato Ayaka", "Cryo", 5),
#     10000003: ("Qin", "Jean", "Anemo", 5),
#     10000004: None,
#     10000005: ("PlayerBoy", "Traveler", "", 5),
#     10000006: ("Lisa", "Electro", 4),
#     10000007: ("PlayerGirl", "Traveler", "", 5),
#     10000008: None,
#     10000009: None,
#     10000010: None,
#     10000011: None,
#     10000012: None,
#     10000013: None,
#     10000014: ("Barbara", "Hydro", 4),
#     10000015: ("Kaeya", "Cryo", 4),
#     10000016: ("Diluc", "Pyro", 5),
#     10000017: None,
#     10000018: None,
#     10000019: None,
#     10000020: ("Razor", "Electro", 4),
#     10000021: ("Ambor", "Amber", "Pyro", 4),
#     10000022: ("Venti", "Anemo", 5),
#     10000023: ("Xiangling", "Pyro", 4),
#     10000024: ("Beidou", "Electro", 4),
#     10000025: ("Xingqiu", "Hydro", 4),
#     10000026: ("Xiao", "Anemo", 5),
#     10000027: ("Ningguang", "Geo", 4),
#     10000028: None,
#     10000029: ("Klee", "Pyro", 5),
#     10000030: ("Zhongli", "Geo", 5),
#     10000031: ("Fischl", "Electro", 4),
#     10000032: ("Bennett", "Pyro", 4),
#     10000033: ("Tartaglia", "Hydro", 5),
#     10000034: ("Noel", "Noelle", "Geo", 4),
#     10000035: ("Qiqi", "Cryo", 5),
#     10000036: ("Chongyun", "Cryo", 4),
#     10000037: ("Ganyu", "Cryo", 5),
#     10000038: ("Albedo", "Geo", 5),
#     10000039: ("Diona", "Cryo", 4),
#     10000040: None,
#     10000041: ("Mona", "Hydro", 5),
#     10000042: ("Keqing", "Electro", 5),
#     10000043: ("Sucrose", "Anemo", 4),
#     10000044: ("Xinyan", "Pyro", 4),
#     10000045: ("Rosaria", "Cryo", 4),
#     10000046: ("Hutao", "Hu Tao", "Pyro", 5),
#     10000047: ("Kazuha", "Kaedehara Kazuha", "Anemo", 5),
#     10000048: ("Feiyan", "Yanfei", "Pyro", 4),
#     10000049: ("Yoimiya", "Pyro", 5),
#     10000050: ("Tohma", "Thoma", "Pyro", 4),
#     10000051: ("Eula", "Cryo", 5),
#     10000052: ("Shougun", "Raiden Shogun", "Electro", 5),
#     10000053: ("Sayu", "Anemo", 4),
#     10000054: ("Kokomi", "Sangonomiya Kokomi", "Hydro", 5),
#     10000055: ("Gorou", "Geo", 4),
#     10000056: ("Sara", "Kujou Sara", "Electro", 4),
#     10000057: ("Itto", "Arataki Itto", "Geo", 5),
#     10000058: ("Yae", "Yae Miko", "Electro", 5),
#     10000059: ("Heizo", "Shikanoin Heizou", "Anemo", 4),
#     10000060: ("Yelan", "Hydro", 5),
#     10000061: None,
#     10000062: ("Aloy", "Cryo", 105),
#     10000063: ("Shenhe", "Cryo", 5),
#     10000064: ("Yunjin", "Yun Jin", "Geo", 4),
#     10000065: ("Shinobu", "Kuki Shinobu", "Electro", 4),
#     10000066: ("Ayato", "Kamisato Ayato", "Hydro", 5),
#     10000067: ("Collei", "Dendro", 4),
#     10000068: ("Dori", "Electro", 4),
#     10000069: ("Tighnari", "Dendro", 5),
#     10000070: ("Nilou", "Hydro", 5),
#     10000071: ("Cyno", "Electro", 5),
#     10000072: ("Candace", "Hydro", 4),
# }
CHARACTER_NAMES: dict[str, dict[int, DBChar]] = {}
