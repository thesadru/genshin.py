"""A simple HTTP client for API endpoints."""
from .components import chronicle, daily, diary, geetest, transaction, wish

__all__ = ["Client"]


class Client(
    chronicle.BattleChronicleClient,
    daily.DailyRewardClient,
    diary.DiaryClient,
    wish.WishClient,
    transaction.TransactionClient,
    geetest.GeetestClient,
):
    """A simple HTTP client for API endpoints."""
