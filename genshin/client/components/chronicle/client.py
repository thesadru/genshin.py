"""Battle chronicle component."""
from . import genshin, honkai, starrail

__all__ = ["BattleChronicleClient"]


class BattleChronicleClient(
    genshin.GenshinBattleChronicleClient,
    honkai.HonkaiBattleChronicleClient,
    starrail.StarRailBattleChronicleClient,
):
    """Battle chronicle component."""
