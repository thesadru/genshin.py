from typing import Any, Sequence

from pydantic import field_validator

from genshin import types
from genshin.models.model import Aliased, APIModel

__all__ = (
    "AccompanyCharacter",
    "AccompanyCharacterAttribute",
    "AccompanyCharacterGame",
    "AccompanyCharacterInfo",
    "AccompanyCharacterProfile",
    "AccompanyResult",
)


class AccompanyCharacterInfo(APIModel):
    """Accompany character info."""

    role_id: int
    game_id: int
    name: str
    brief_name: str
    topic_id: int
    game_name: str


class AccompanyCharacterProfile(APIModel):
    """Accompany character color and images."""

    card_color: str
    bg_dark_color: str
    bg_light_color: str
    bg_card_color: str

    card_image: str = Aliased("card_img_url")
    video: str = Aliased("full_screen_video_265")
    icon: str = Aliased("icon_url")


class AccompanyCharacter(APIModel):
    """Accompany character."""

    info: AccompanyCharacterInfo = Aliased("basic")
    profile: AccompanyCharacterProfile = Aliased("attr_profile")
    attribute_ids: Sequence[int]


class AccompanyCharacterAttribute(APIModel):
    """Accompany character attribute."""

    id: int
    icon: str = Aliased("icon_url")
    corner_icon: str = Aliased("corner_icon_url")


class AccompanyCharacterGame(APIModel):
    """Accompany character game."""

    attributes: Sequence[Sequence[AccompanyCharacterAttribute]] = Aliased("attribute_group_list")
    id: int = Aliased("game_id")
    icon: str = Aliased("game_icon")
    characters: Sequence[AccompanyCharacter] = Aliased("role_list")

    @field_validator("attributes", mode="before")
    def __unnest_attributes(cls, v: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        return [group["attribute_list"] for group in v]

    @property
    def game(self) -> types.Game:
        if self.id == 2:
            return types.Game.GENSHIN
        if self.id == 6:
            return types.Game.STARRAIL
        if self.id == 8:
            return types.Game.ZZZ

        raise ValueError(f"Unknown game ID: {self.id}")


class AccompanyResult(APIModel):
    """Accompany result."""

    accompany_days: int
    points_increased: int = Aliased("increase_accompany_point")
