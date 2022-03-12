"""A simple HTTP client for API endpoints."""
from .components import chronicle, geetest, wish

__all__ = ["Client"]


class Client(
    chronicle.BattleChronicleClient,
    wish.WishClient,
    geetest.GeetestClient,
):
    """A simple HTTP client for API endpoints."""
