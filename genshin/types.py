"""Types used in the library."""
import enum


class Region(enum.Enum):
    """Region to get data from."""

    UNKNOWN = 0
    """Unknown region."""

    OVERSEAS = 1
    """Applies to all overseas APIs."""

    CHINESE = 2
    """Applies to all chinese mainland APIs."""


class Game(enum.Enum):
    """Hoyoverse game."""

    GENSHIN = 1
    """Genshin Impact"""

    HONKAI = 2
    """Honkai Impact 3rd"""
