import datetime

from genshin.models.model import Aliased, APIModel

__all__ = ("WebEvent",)


class WebEvent(APIModel):
    """Hoyolab web event model."""

    id: int
    name: str
    description: str = Aliased("desc")

    start_time: datetime.datetime = Aliased("start")
    end_time: datetime.datetime = Aliased("end")
    create_time: datetime.datetime = Aliased("create_at")

    web_path: str
    app_path: str

    banner: str = Aliased("banner_url")
    status: int

    @property
    def url(self) -> str:
        if "https" in self.web_path:
            return self.web_path
        return f"https://www.hoyolab.com{self.web_path}"
