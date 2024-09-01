"""Public genshin announcement models."""

import datetime
import typing

from genshin.models.model import Aliased, APIModel, Unique

__all__ = ["Announcement"]


class Announcement(APIModel, Unique):
    """Announcement model."""

    id: int = Aliased("ann_id")
    title: str
    subtitle: str
    banner: str
    content: str
    img: typing.Optional[str] = None

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
