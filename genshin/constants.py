"""Constants for data completions and assertions"""
from typing import Dict, NamedTuple

__all__ = ["CHARACTER_NAMES", "LANGS"]


class DBChar(NamedTuple):
    id: int
    icon_name: str  # standardized icon name
    name: str  # english name
    element: str
    rarity: int


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
    10000057: ("Itto", "Arataki Itoo", "Geo", 5),
    # collab:
    10000062: ("Aloy", "Aloy", "Cryo", 105),
}
CHARACTER_NAMES: Dict[int, DBChar] = {
    id: DBChar(id, *data) for id, data in _character_names.items() if data is not None
}


class DBSuit(NamedTuple):
    id: int
    name: str  # english (battlesuit) name
    icon_name: str  # standardized icon name
    character_name: str
    type: str
    base_rank: str


_character_names = {
    101: ("White Comet", "KianaC2", "Kiana Kaslana", "MECH", "B"),
    102: ("Valkyrie Ranger", "KianaC1", "Kiana Kaslana", "MECH", "A"),
    103: ("Knight Moonbeam", "KianaC4", "Kiana Kaslana", "BIO", "S"),
    104: ("Divine Prayer", "KianaC3", "Kiana Kaslana", "PSY", "A"),
    105: ("Herrscher of Flamescion", "KianaC6", "Kiana Kaslana", "PSY", "S"),
    111: ("Sixth Serenade", "KallenC1", "Kallen Kaslana", "PSY", "S"),
    112: ("Ritual Imayoh", "KallenC2", "Kallen Kaslana", "MECH", "A"),
    113: ("Herrscher of the Void", "KianaC5", "Kiana Kaslana", "BIO", "S"),
    114: ("Sündenjäger", "KallenC3", "Kiana Kaslana", "BIO", "A"),
    201: ("Crimson Impulse", "MeiC2", "Raiden Mei", "BIO", "B"),
    202: ("Shadow Dash", "MeiC3", "Raiden Mei", "MECH", "A"),
    203: ("Valkyrie Bladestrike", "MeiC1", "Raiden Mei", "BIO", "A"),
    204: ("Lightning Empress", "MeiC4", "Raiden Mei", "PSY", "S"),
    205: ("Herrscher of Thunder", "MeiC5", "Raiden Mei", "PSY", "S"),
    211: ("Gyakushinn Miko", "SakuraC1", "Yae Sakura", "BIO", "A"),
    212: ("Goushinnso Memento", "SakuraC2", "Yae Sakura", "MECH", "S"),
    213: ("Flame Sakitama", "SakuraC3", "Yae Sakura", "BIO", "A"),
    214: ("Darkbolt Jonin", "SakuraC4", "Yae Sakyra", "BIO", "A"),
    301: ("Valkyrie Chariot", "BronyaC1", "Bronya Zaychik", "PSY", "B"),
    302: ("Yamabuki Armor", "BronyaC2", "Bronya Zaychik", "PSY", "A"),
    303: ("Snowy Sniper", "BronyaC3", "Bronya Zaychik", "BIO", "A"),
    304: ("Dimension Breaker", "BronyaC4", "Bronya Zaychik", "MECH", "S"),
    311: ("Wolf's Dawn", "BronyaC5", "Bronya Zaychik", "PSY", "A"),
    312: ("Black Nucleus", "BronyaC6", "Bronya Zaychik", "BIO", "S"),
    313: ("Herrscher of Reason", "BronyaC7", "Bronya Zaychik", "MECH", "S"),
    314: ("Haxxor Bunny", "BronyaC8", "Bronya Zaychik", "PSY", "A"),
    401: ("Valkyrie Triumph", "HimekoC1", "Murata Himeko", "BIO", "A"),
    402: ("Scarlet Fusion", "HimekoC2", "Murata Himeko", "MECH", "A"),
    403: ("Battle Storm", "HimekoC3", "Murata Himeko", "BIO", "B"),
    404: ("Blood Rose", "HimekoC4", "Murata Himeko", "PSY", "S"),
    411: ("Kriegsmesser", "HimekoC5", "Murata Himeko", "PSY", "A"),
    412: ("Vermilion Knight: Eclipse", "HimekoC6", "Murata Himeko", "MECH", "S"),
    421: ("Blueberry Blitz", "TwinC1", "Liliya Olyenyeva", "MECH", "A"),
    422: ("Molotov Cherry", "TwinC2", "Rozaliya Olyenyeva", "PSY", "S"),
    501: ("Valkyrie Pledge", "TheresaC1", "Theresa Apocalypse", "PSY", "A"),
    502: ("Violet Executer", "TheresaC2", "Theresa Apocalypse", "MECH", "S"),
    503: ("Sakuno Rondo", "TheresaC3", "Theresa Apocalypse", "PSY", "A"),
    504: ("Celestial Hymn", "TheresaC4", "Theresa Apocalypse", "BIO", "S"),
    506: ("Starlit Astrologos", "TheresaC6", "Theresa Apocalypse", "BIO", "A"),
    511: ("Luna Kindred", "TheresaC5", "Theresa Apocalypse", "BIO", "A"),
    601: ("Valkyrie Accipiter", "FukaC1", "Fu Hua", "PSY", "A"),
    602: ("Shadow Knight", "FukaC2", "Fu Hua", "MECH", "S"),
    603: ("Night Squire", "FukaC3", "Fu Hua", "BIO", "A"),
    604: ("Phoenix", "FukaC4", "Fu Hua", "PSY", "S"),
    611: ("Azure Empyrea", "FukaC5", "Fu Hua", "PSY", "S"),
    612: ("Herrscher of Sentience", "FukaC6", "Fu Hua", "BIO", "S"),
    702: ("Phantom Iron", "RitaC2", "Rita Rossweise", "MECH", "A"),
    703: ("Umbral Rose", "RitaC3", "Rita Rossweise", "PSY", "A"),
    704: ("Argent Knight: Artemis", "RitaC4", "Rita Rossweise", "BIO", "S"),
    705: ("Fallen Rosemary", "RitaC5", "Rita Rossweise", "QUA", "S"),
    711: ("Swallowtail Phantasm", "SeeleC1", "Seele Vollerei", "QUA", "A"),
    712: ("Stygian Nymph", "SeeleC2", "Seele Vollerei", "QUA", "S"),
    713: ("Starchasm Nyx", "SeeleC3", "Seele Vollerei", "QUA", "S"),
    801: ("Valkyrie Gloria", "DurandalC1", "Durandal", "QUA", "A"),
    802: ("Bright Knight: Excelsis", "DurandalC2", "Durandal", "MECH", "S"),
    803: ("Dea Anchora", "DurandalC3", "Durandal", "BIO", "S"),
    901: ("Blazing Hope", "AsukaC1", "Asuka Langley", "BIO", "A"),
    2101: ("Prinzessin der Verurteilung!", "FischlC1", "Fischl", "BIO", "A"),
    2201: ("Miss Pink Elf♪", "ElysiaC1", "Elysia", "PSY", "S"),
    2301: ("Infinite Ouroboros", "MobiusC1", "Mobius", "MECH", "S"),
    2401: ("Midnight Absinthe", "RavenC1", "Natasha Cioara", "IMG", "A"),
    2501: ("Sweet 'n' Spicy", "CaroleC1", "Carole Pepper", "MECH", "A"),
}
BATTLESUIT_NAMES = {
    id: DBSuit(id, *data) for id, data in _character_names.items() if data is not None
}


# NOTE: This is entirely optional; just felt like the signets were beyond useless as just an id and a pic,
#       so I yoinked the name and description from the game. If this is considered outside of the scope of
#       this project I'll just remove it, no sweat.

tier_2_signet_fmt = "Portals carrying Signets of {} appear more often."
tier_3_signet_fmt = "Grants 1 extra level when choosing a Signet of {}."


class RemembranceSigil(NamedTuple):

    id: int
    name: str
    rarity: int
    description: str


_remembrance_sigils = {
    119301: ("The MOTH Insignia", 1, "Restores 10% HP after battle."),
    119302: (
        "Home Lost",
        1,
        "Grants 3 portal resets but locks Remembrance Sigil and Support Valkyries",
    ),
    119303: ("False Hope", 1, "Valkyrie receives 50% less Total DMG when debuffed."),
    119304: ("Tin Flask", 1, "Flame-Chaser support skills are triggered more often"),
    119305: (
        "Ruined Legacy",
        1,
        "Grants 30 bonus intial SP but consumes 10% current HP after battle.",
    ),
    119306: ("Burden", 2, tier_2_signet_fmt.format("Deliverance")),
    119307: ("Gold Goblet", 2, tier_2_signet_fmt.format("Gold")),
    119308: ("Mad King's Mask", 2, tier_2_signet_fmt.format("Decimation")),
    119309: ("Light as a Bodhi Leaf", 2, tier_2_signet_fmt.format("Bodhi")),
    119310: ("Forget-Me-Not", 2, tier_2_signet_fmt.format("Setsuna")),
    119311: ("Forbidden Seed", 2, tier_2_signet_fmt.format("Infinity")),
    119312: ("Memory", 2, tier_2_signet_fmt.format("Vicissitude")),
    119313: ("Crystal Rose", 2, "Portals Carrying Signets of ■■ appear more often"),
    119314: (
        "Abandoned",
        3,
        f"{tier_3_signet_fmt.format('Deliverance')} Killing enemies reduces Ultimate CD by 30%",
    ),
    119315: (
        "Good Old Days",
        3,
        f"{tier_3_signet_fmt.format('Gold')} Grants 1 extra level when choosing a Signet of Gold",
    ),
    119316: (
        "Shattered Shackles",
        3,
        f"{tier_3_signet_fmt.format('Decimation')} At below 33% HP, Valkyrie is immune to most debuffs; at below 20% HP, Valkyrie will not be interrupted when hit.",
    ),
    119317: (
        "Heavy as a Million Lives",
        3,
        f"{tier_3_signet_fmt.format('Bodhi')} Combo count will not be reset; the first hit that lands grants an additional 50 combo count.",
    ),
    119318: (
        "Stained Sakura",
        3,
        f"{tier_3_signet_fmt.format('Setsuna')} When signet Setsuna Blade: Sakura Screen is active, every time Sakura Screen is triggered, its DMG conversion ratio increases by 10%.",
    ),
    119319: (
        "The First Scale",
        3,
        f"{tier_3_signet_fmt.format('Infinity')} When the Signets of Infinite [X] are active, Valkyrie will enter a 3-sec Mind Sync when a battle starts.",
    ),
    119320: (
        "Resolve",
        3,
        f"{tier_3_signet_fmt.format('Vicissitude')} When signet Vivid Vicissitude is active, Soldier's Resolve starts with 1 more stack and grands temporary invincibility when blocking DMG.",
    ),
    119321: ("Thorny Crown", 3, "???"),
}
REMEMBRANCE_SIGILS = {id: RemembranceSigil(id, *data) for id, data in _remembrance_sigils.items()}


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
