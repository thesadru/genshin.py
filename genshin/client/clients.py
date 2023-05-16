"""A simple HTTP client for API endpoints."""
from .components import (
    calculator,
    chronicle,
    daily,
    diary,
    gacha,
    geetest,
    hoyolab,
    lineup,
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
    lineup.LineupClient,
    teapot.TeapotClient,
    wiki.WikiClient,
    gacha.WishClient,
    transaction.TransactionClient,
    geetest.GeetestClient,
):
    """A simple HTTP client for API endpoints."""
