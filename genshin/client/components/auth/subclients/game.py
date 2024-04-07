"""Game sub client for AuthClient.

Covers OS and CN game auth endpoints.
"""

from genshin.client.components import base

__all__ = ["GameAuthClient"]


class GameAuthClient(base.BaseClient):
    """Game sub client for AuthClient."""
