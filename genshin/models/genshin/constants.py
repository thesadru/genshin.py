"""Genshin model constants."""
import typing

__all__ = ["CHARACTER_NAMES", "DBChar"]


class DBChar(typing.NamedTuple):
    """Partial genshin character data."""

    id: int
    icon_name: str  # standardized icon name
    name: str  # english name
    element: str
    rarity: int

    guessed: bool = False


_character_names = {
    10000001: None,
    10000002: ("Ayaka", "Kamisato Ayaka", "Cryo", 5),
    10000003: ("Qin", "Jean", "Anemo", 5),
    10000004: None,
    10000005: ("PlayerBoy", "Traveler", "", 5),
    10000006: ("Lisa", "Lisa", "Electro", 4),
    10000007: ("PlayerGirl", "Traveler", "", 5),
    10000008: None,
    10000009: None,
    10000010: None,
    10000011: None,
    10000012: None,
    10000013: None,
    10000014: ("Barbara", "Barbara", "Hydro", 4),
    10000015: ("Kaeya", "Kaeya", "Cryo", 4),
    10000016: ("Diluc", "Diluc", "Pyro", 5),
    10000017: None,
    10000018: None,
    10000019: None,
    10000020: ("Razor", "Razor", "Electro", 4),
    10000021: ("Ambor", "Amber", "Pyro", 4),
    10000022: ("Venti", "Venti", "Anemo", 5),
    10000023: ("Xiangling", "Xiangling", "Pyro", 4),
    10000024: ("Beidou", "Beidou", "Electro", 4),
    10000025: ("Xingqiu", "Xingqiu", "Hydro", 4),
    10000026: ("Xiao", "Xiao", "Anemo", 5),
    10000027: ("Ningguang", "Ningguang", "Geo", 4),
    10000028: None,
    10000029: ("Klee", "Klee", "Pyro", 5),
    10000030: ("Zhongli", "Zhongli", "Geo", 5),
    10000031: ("Fischl", "Fischl", "Electro", 4),
    10000032: ("Bennett", "Bennett", "Pyro", 4),
    10000033: ("Tartaglia", "Tartaglia", "Hydro", 5),
    10000034: ("Noel", "Noelle", "Geo", 4),
    10000035: ("Qiqi", "Qiqi", "Cryo", 5),
    10000036: ("Chongyun", "Chongyun", "Cryo", 4),
    10000037: ("Ganyu", "Ganyu", "Cryo", 5),
    10000038: ("Albedo", "Albedo", "Geo", 5),
    10000039: ("Diona", "Diona", "Cryo", 4),
    10000040: None,
    10000041: ("Mona", "Mona", "Hydro", 5),
    10000042: ("Keqing", "Keqing", "Electro", 5),
    10000043: ("Sucrose", "Sucrose", "Anemo", 4),
    10000044: ("Xinyan", "Xinyan", "Pyro", 4),
    10000045: ("Rosaria", "Rosaria", "Cryo", 4),
    10000046: ("Hutao", "Hu Tao", "Pyro", 5),
    10000047: ("Kazuha", "Kaedehara Kazuha", "Anemo", 5),
    10000048: ("Feiyan", "Yanfei", "Pyro", 4),
    10000049: ("Yoimiya", "Yoimiya", "Pyro", 5),
    10000050: ("Tohma", "Thoma", "Pyro", 4),
    10000051: ("Eula", "Eula", "Cryo", 5),
    10000052: ("Shougun", "Raiden Shogun", "Electro", 5),
    10000053: ("Sayu", "Sayu", "Anemo", 4),
    10000054: ("Kokomi", "Sangonomiya Kokomi", "Hydro", 5),
    10000055: ("Gorou", "Gorou", "Geo", 4),
    10000056: ("Sara", "Kujou Sara", "Electro", 4),
    10000057: ("Itto", "Arataki Ito", "Geo", 5),
    10000058: ("YaeMiko", "Yae Miko", "Electro", 5),
    10000059: None,
    10000060: None,
    10000061: None,
    10000062: ("Aloy", "Aloy", "Cryo", 105),
    10000063: ("Shenhe", "Shenhe", "Cryo", 5),
    10000064: ("YunJin", "Yun Jin", "Geo", 4),
}
CHARACTER_NAMES: typing.Dict[int, DBChar] = {
    id: DBChar(id, *data) for id, data in _character_names.items() if data is not None
}
