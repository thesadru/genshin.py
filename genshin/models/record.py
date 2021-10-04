from typing import Any
from pydantic import BaseModel, Field

class RecordCardData(BaseModel):
    name: str
    value: str

class RecordCard(BaseModel):
    uid: int = Field(alias="game_role_id")
    level: int
    nickname: str
    region: str
    region_name: str
    
    data: list[RecordCardData]
    
    # unknown menaing
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
