from datetime import datetime
from typing import Literal

from pydantic import Field

from genshin import models


__all__ = ["TransactionKind", "BaseTransaction", "Transaction", "ItemTransaction"]

TransactionKind = Literal["primogem", "crystal", "resin", "artifact", "weapon"]

class BaseTransaction(models.APIModel, models.Unique):
    """A genshin transaction"""

    kind: TransactionKind

    id: int
    uid: int
    time: datetime
    amount: int = Field(galias="add_num")
    reason_id: int
    reason: str = ""


class Transaction(BaseTransaction):
    """A genshin transaction of currency"""

    kind: Literal["primogem", "crystal", "resin"]


class ItemTransaction(BaseTransaction):
    """A genshin transaction of artifacts or weapons"""

    kind: Literal["artifact", "weapon"]

    name: str
    rarity: int = Field(galias="rank")
