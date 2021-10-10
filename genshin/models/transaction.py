from datetime import datetime
from typing import Literal

from pydantic import Field

from .base import GenshinModel


class Transaction(GenshinModel):
    kind: Literal["primogem", "crystal", "resin"]

    id: int
    uid: int
    time: datetime
    amount: int = Field(alias="add_num")
    reason_id: int = Field(alias="reason")
    reason: str = Field("", alias="reason_str")


class ItemTransaction(Transaction):
    kind: Literal["artifact", "weapon"]

    name: str
    rarity: int = Field(alias="rank")
