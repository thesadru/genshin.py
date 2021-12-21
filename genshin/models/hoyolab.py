import re
from enum import IntEnum

from pydantic import Field, validator

from genshin import models

__all__ = [
    "Gender",
    "SearchUser",
]


class Gender(IntEnum):
    unknown = 0
    male = 1
    female = 2
    other = 3


class SearchUser(models.APIModel):
    """A user from a search result"""

    hoyolab_uid: int = Field(galias="uid")
    nickname: str
    introduction: str = Field(galias="introduce")
    avatar_id: int = Field(galias="avatar")
    gender: Gender
    icon: str = Field(galias="avatar_url")

    @validator("nickname")
    def __remove_tag(cls, v: str) -> str:
        return re.sub(r"<.+?>", "", v)
