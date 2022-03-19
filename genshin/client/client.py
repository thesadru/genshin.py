"""A simple HTTP client for API endpoints."""
from .components import chronicle, daily, diary, geetest, transaction, wish
from .components.calculator import client

__all__ = ["Client"]


class Client(
    chronicle.BattleChronicleClient,
    daily.DailyRewardClient,
    client.CalculatorClient,
    diary.DiaryClient,
    wish.WishClient,
    transaction.TransactionClient,
    geetest.GeetestClient,
):
    """A simple HTTP client for API endpoints."""
