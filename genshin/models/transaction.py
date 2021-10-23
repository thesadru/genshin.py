from datetime import datetime
from typing import Literal

from pydantic import Field

from .base import GenshinModel

TransactionKind = Literal["primogem", "crystal", "resin", "artifact", "weapon"]


class Transaction(GenshinModel):
    """A genshin transaction of currency"""

    kind: Literal["primogem", "crystal", "resin"]

    id: int
    uid: int
    time: datetime
    amount: int = Field(galias="add_num")
    reason_id: int = Field(galias="reason")
    reason: str = Field("", galias="reason_str")


class ItemTransaction(Transaction):
    """A genshin transaction of artifacts or weapons"""

    kind: Literal["artifact", "weapon"]

    name: str
    rarity: int = Field(galias="rank")
