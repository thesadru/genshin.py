"""Genshin transaction models."""

import enum
import typing

from genshin.models.model import Aliased, APIModel, TZDateTime, Unique

__all__ = ["BaseTransaction", "ItemTransaction", "Transaction", "TransactionKind"]


class TransactionKind(str, enum.Enum):
    """Possible kind of transaction."""

    PRIMOGEM = "primogem"
    """Primogem currency."""

    CRYSTAL = "crystal"
    """Genesis crystal currency."""

    RESIN = "resin"
    """Resin currency."""

    ARTIFACT = "artifact"
    """Artifact items from domains."""

    WEAPON = "weapon"
    """Weapon items from domains and wishes."""


class BaseTransaction(APIModel, Unique):
    """Genshin transaction."""

    kind: TransactionKind

    id: int
    time: TZDateTime = Aliased("datetime")
    amount: int = Aliased("add_num")
    reason: str = Aliased("reason")


class Transaction(BaseTransaction):
    """Genshin transaction of currency."""

    kind: typing.Literal[TransactionKind.PRIMOGEM, TransactionKind.CRYSTAL, TransactionKind.RESIN]


class ItemTransaction(BaseTransaction):
    """Genshin transaction of artifacts or weapons."""

    kind: typing.Literal[TransactionKind.ARTIFACT, TransactionKind.WEAPON]

    name: str
    rarity: int = Aliased("quality")
