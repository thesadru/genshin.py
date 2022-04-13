"""Battle chronicle component."""
from . import genshin, honkai

__all__ = ["BattleChronicleClient"]


class BattleChronicleClient(
    genshin.GenshinBattleChronicleClient,
    honkai.HonkaiBattleChronicleClient,
):
    """Battle chronicle component."""
