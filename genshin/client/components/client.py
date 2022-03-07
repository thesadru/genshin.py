"""A simple HTTP client for API endpoints."""
from . import chronicle

__all__ = ["Client"]


class Client(
    chronicle.BattleChronicleClient,
):
    """A simple HTTP client for API endpoints."""
