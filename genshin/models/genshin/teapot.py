"""Genshin serenitea pot replica display models."""

from __future__ import annotations

import datetime
import typing

if typing.TYPE_CHECKING:
    import pydantic.v1 as pydantic
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
        import pydantic

from genshin.models.model import Aliased, APIModel, Unique

__all__ = [
    "TeapotReplica",
    "TeapotReplicaAuthor",
    "TeapotReplicaBlueprint",
    "TeapotReplicaStats",
]


class TeapotReplicaAuthor(APIModel):
    """Teapot replica author."""

    id: int = Aliased("user_id")
    nickname: str
    icon: str = Aliased("avatar")


class TeapotReplicaStats(APIModel):
    """Teapot replica stats."""

    diggs: int = Aliased("digg_cnt")
    saves: int = Aliased("store_cnt")
    views: int = Aliased("view_cnt")
    replies: int = Aliased("reply_cnt")
    shares: int = Aliased("share_cnt")
    copies: int = Aliased("copy_cnt")


class TeapotReplicaBlueprint(APIModel):
    """Teapot replica blueprint."""

    share_code: int
    region: str
    module_id: str
    block_id: str
    is_invalid: bool


class TeapotReplica(APIModel, Unique):
    """Genshin serenitea pot replica."""

    post_id: str
    title: str
    content: str
    images: typing.List[str] = Aliased("imgs")
    created_at: datetime.datetime
    stats: TeapotReplicaStats
    lang: str  # type: ignore

    author: TeapotReplicaAuthor

    view_type: int
    sub_type: int
    blueprint: TeapotReplicaBlueprint
    video: typing.Optional[str]

    has_more_content: bool
    token: str

    @pydantic.validator("images", pre=True)
    def __extract_urls(cls, images: typing.Sequence[typing.Any]) -> typing.Sequence[str]:
        return [image if isinstance(image, str) else image["url"] for image in images]

    @pydantic.validator("video", pre=True)
    def __extract_url(cls, video: typing.Any) -> typing.Optional[str]:
        if isinstance(video, str):
            return video

        return video["url"] if video else None
