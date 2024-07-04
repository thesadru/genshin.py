"""Battle chronicle component."""

from . import genshin, honkai, starrail, zzz

__all__ = ["BattleChronicleClient"]


class BattleChronicleClient(
    genshin.GenshinBattleChronicleClient,
    honkai.HonkaiBattleChronicleClient,
    starrail.StarRailBattleChronicleClient,
    zzz.ZZZBattleChronicleClient,
):
    """Battle chronicle component."""
