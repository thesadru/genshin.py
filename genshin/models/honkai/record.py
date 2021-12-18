from pydantic import Field

from ..base import APIModel

__all__ = ("UserInfo",)


class UserInfo(APIModel):

    nickname: str
    region: str
    level: int
    icon: str = Field(galias="AvatarUrl")
