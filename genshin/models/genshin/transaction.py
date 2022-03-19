"""Genshin transaction models."""

import datetime
import enum
import typing

from genshin.models.model import Aliased, APIModel, Unique

__all__ = ["BaseTransaction", "ItemTransaction", "Transaction", "TransactionKind"]


class TransactionKind(str, enum.Enum):
    """Possible kind of transaction."""

    PRIMOGEM = "primogem"
    """Primogem currency."""

    CRYSTAL = "crystal"
    """Genesis crystal currenncy."""

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
    uid: int
    time: datetime.datetime
    amount: int = Aliased("add_num")
    reason_id: int = Aliased("reason")

    # TODO: parse reason_id using i18n


class Transaction(BaseTransaction):
    """Genshin transaction of currency."""

    kind: typing.Literal[TransactionKind.PRIMOGEM, TransactionKind.CRYSTAL, TransactionKind.RESIN]


class ItemTransaction(BaseTransaction):
    """Genshin transaction of artifacts or weapons."""

    kind: typing.Literal[TransactionKind.ARTIFACT, TransactionKind.WEAPON]

    name: str
    rarity: int = Aliased("rank")
