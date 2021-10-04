from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator


class BannerType(int, Enum):
    novice = 100
    permanent = 200
    character = 301
    weapon = 302
    

class Wish(BaseModel):
    uid: int
    
    id: int
    type: str = Field(alias="item_type")
    name: str
    rarity: int = Field(alias="rank_type")
    time: datetime
    
    banner_type: BannerType = Field(alias="gacha_type")
    banner_name: str
    
    @validator("banner_type", pre=True)
    def __cast_banner_type(cls, v):
        return int(v)
