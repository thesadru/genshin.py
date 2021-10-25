from datetime import datetime
from typing import Literal

from pydantic import Field, root_validator

from .base import GenshinModel

TransactionKind = Literal["primogem", "crystal", "resin", "artifact", "weapon"]

class BaseTransaction(GenshinModel):
    """A genshin transaction of currency"""

    kind: TransactionKind

    id: int
    uid: int
    time: datetime
    amount: int = Field(galias="add_num")
    reason_id: int = Field(galias="reason")
    reason: str = Field("", galias="reason_str")
    
    @root_validator()
    def __check_for_validation(cls, values):
        # In case we try to validate this exact model reason & reason_id can get mixed up
        if "reason_id" in values:
            values["reason"], values["reason_str"] = values["reason_id"], values["reason"]
        return values
    

class Transaction(BaseTransaction):

    kind: Literal["primogem", "crystal", "resin"]

class ItemTransaction(BaseTransaction):
    """A genshin transaction of artifacts or weapons"""

    kind: Literal["artifact", "weapon"]

    name: str
    rarity: int = Field(galias="rank")
