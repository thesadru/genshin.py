"""A simple HTTP client for API endpoints."""

from .components import (
    calculator,
    chronicle,
    daily,
    diary,
    gacha,
    auth,
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
    auth.AuthClient,
):
    """A simple HTTP client for API endpoints."""
