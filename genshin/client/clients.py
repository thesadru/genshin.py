"""A simple HTTP client for API endpoints."""

from .components import (
    auth,
    calculator,
    chronicle,
    daily,
    diary,
    gacha,
    hoyolab,
    teapot,
    transaction,
    wiki,
)

__all__ = ["Client"]


class Client(
    chronicle.BattleChronicleClient,
    hoyolab.HoyolabClient,
    daily.DailyRewardClient,
    calculator.CalculatorClient,
    diary.DiaryClient,
    teapot.TeapotClient,
    wiki.WikiClient,
    gacha.WishClient,
    transaction.TransactionClient,
    auth.AuthClient,
):
    """A simple HTTP client for API endpoints."""
