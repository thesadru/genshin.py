"""A simple HTTP client for API endpoints."""
from .components import (
    calculator,
    chronicle,
    daily,
    diary,
    geetest,
    hoyolab,
    transaction,
    wiki,
    wish,
)

__all__ = ["Client"]


class Client(
    chronicle.BattleChronicleClient,
    hoyolab.HoyolabClient,
    daily.DailyRewardClient,
    calculator.CalculatorClient,
    diary.DiaryClient,
    wiki.WikiClient,
    wish.WishClient,
    transaction.TransactionClient,
    geetest.GeetestClient,
):
    """A simple HTTP client for API endpoints."""
