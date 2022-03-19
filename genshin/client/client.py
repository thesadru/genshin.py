"""A simple HTTP client for API endpoints."""
from .components import (
    calculator,
    chronicle,
    daily,
    diary,
    geetest,
    hoyolab,
    transaction,
    wish,
)

__all__ = ["Client"]


class Client(
    chronicle.BattleChronicleClient,
    hoyolab.HoyolabClient,
    daily.DailyRewardClient,
    calculator.CalculatorClient,
    diary.DiaryClient,
    wish.WishClient,
    transaction.TransactionClient,
    geetest.GeetestClient,
):
    """A simple HTTP client for API endpoints."""
