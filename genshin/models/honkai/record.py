from genshin import models
from pydantic import Field

__all__ = ["UserInfo"]


class UserInfo(models.APIModel):

    nickname: str
    region: str
    level: int
    icon: str = Field(galias="AvatarUrl")
