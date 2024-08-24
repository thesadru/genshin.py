"""Public genshin announcement models."""

import datetime

import pydantic

from genshin.models.model import APIModel

__all__ = ["Announcement"]


class Announcement(APIModel):
    """Announcement model."""

    id: int = pydantic.Field(alias="ann_id")
    title: str
    subtitle: str
    banner: str
    content: str

    type_label: str
    type: int
    tag_icon: str

    login_alert: bool
    remind: bool
    alert: bool
    remind_ver: int
    extra_remind: bool

    start_time: datetime.datetime
    end_time: datetime.datetime
    tag_start_time: datetime.datetime
    tag_end_time: datetime.datetime

    lang: str  # type: ignore
    has_content: bool
