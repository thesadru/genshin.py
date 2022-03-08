"""A simple HTTP client for API endpoints."""
from . import chronicle, geetest

__all__ = ["Client"]


class Client(
    chronicle.BattleChronicleClient,
    geetest.GeetestClient,
):
    """A simple HTTP client for API endpoints."""
