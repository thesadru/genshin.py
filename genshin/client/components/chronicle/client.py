"""Battle chronicle component."""
from . import genshin, honkai


class BattleChronicleClient(
    genshin.GenshinBattleChronicleClient,
    honkai.HonkaiBattleChronicleClient,
):
    """Battle chronicle component."""
