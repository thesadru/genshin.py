from typing import Any
from pydantic import BaseModel, Field

class GenshinAccount(BaseModel):
    uid: int = Field(alias="game_uid")
    level: int
    nickname: str
    server: str = Field(alias="region")
    server_name: str = Field(alias="region_name")
    
    # unknown meaning
    biz: str = Field(alias="game_biz")
    chosen: bool = Field(alias="is_chosen")
    official: bool = Field(alias="is_official")

class RecordCardData(BaseModel):
    name: str
    value: str

class RecordCard(BaseModel):
    uid: int = Field(alias="game_role_id")
    level: int
    nickname: str
    server: str = Field(alias="region")
    server_name: str= Field(alias="region_name")
    
    data: list[RecordCardData]
    
    # unknown meaning
    background_image: str
    has_uid: bool = Field(alias="has_role")
    public: bool = Field(alias="is_public")

    @property
    def days_active(self):
        return int(self.data[0].value)
    
    @property
    def characters(self):
        return int(self.data[1].value)
    
    @property
    def achievements(self):
        return int(self.data[2].value)
    
    @property
    def spiral_abyss(self):
        return self.data[3].value
