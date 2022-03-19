"""A simple HTTP client for API endpoints."""
from .components import chronicle, daily, diary, geetest, wish

__all__ = ["Client"]


class Client(
    chronicle.BattleChronicleClient,
    daily.DailyRewardClient,
    diary.DiaryClient,
    wish.WishClient,
    geetest.GeetestClient,
):
    """A simple HTTP client for API endpoints."""
