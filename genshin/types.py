"""Types used in the library."""
import enum
import typing

if typing.TYPE_CHECKING:
    from genshin.models.model import Unique

__all__ = ["Game", "IDOr", "Region"]

UniqueT = typing.TypeVar("UniqueT", bound="Unique")


class Region(str, enum.Enum):
    """Region to get data from."""

    OVERSEAS = "os"
    """Applies to all overseas APIs."""

    CHINESE = "cn"
    """Applies to all chinese mainland APIs."""


class Game(str, enum.Enum):
    """Hoyoverse game."""

    GENSHIN = "genshin"
    """Genshin Impact"""

    HONKAI = "honkai3rd"
    """Honkai Impact 3rd"""


IDOr = typing.Union[int, UniqueT]
"""Allows partial objects."""
