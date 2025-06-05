"""A simple HTTP client for API endpoints."""

from .components import (
    auth,
    calculator,
    chronicle,
    daily,
    diary,
    gacha,
    hoyolab,
    hsr_lineup,
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
    hsr_lineup.HSRLineupClient,
):
    """A simple HTTP client for API endpoints."""
