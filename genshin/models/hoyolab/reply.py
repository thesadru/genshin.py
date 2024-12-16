from genshin.models.model import APIModel

__all__ = ("Reply",)


class Reply(APIModel):
    """Reply model."""

    post_id: int
    reply_id: int
    content: str
