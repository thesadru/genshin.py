from pydantic import Field

from .base import GenshinModel

__all__ = ("UserInfo",)


class UserInfo(GenshinModel):

    nickname: str
    region: str
    level: int
    icon: str = Field(galias="AvatarUrl")
