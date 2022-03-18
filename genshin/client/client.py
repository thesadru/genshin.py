"""A simple HTTP client for API endpoints."""
from .components import chronicle, daily, geetest, wish

__all__ = ["Client"]


class Client(
    chronicle.BattleChronicleClient,
    wish.WishClient,
    geetest.GeetestClient,
    daily.DailyRewardClient,
):
    """A simple HTTP client for API endpoints."""
