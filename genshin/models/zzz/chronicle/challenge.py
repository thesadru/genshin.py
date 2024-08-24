import datetime
import typing

import pydantic

from genshin.constants import CN_TIMEZONE
from genshin.models.model import APIModel
from genshin.models.zzz.character import ZZZElementType

__all__ = (
    "ShiyuDefense",
    "ShiyuDefenseBangboo",
    "ShiyuDefenseBuff",
    "ShiyuDefenseCharacter",
    "ShiyuDefenseFloor",
    "ShiyuDefenseMonster",
    "ShiyuDefenseNode",
)


class ShiyuDefenseBangboo(APIModel):
    """Shiyu Defense bangboo model."""

    id: int
    rarity: typing.Literal["S", "A"]
    level: int

    @property
    def icon(self) -> str:
        return f"https://act-webstatic.hoyoverse.com/game_record/zzz/bangboo_square_avatar/bangboo_square_avatar_{self.id}.png"


class ShiyuDefenseCharacter(APIModel):
    """Shiyu Defense character model."""

    id: int
    level: int
    rarity: typing.Literal["S", "A"]
    element: ZZZElementType = pydantic.Field(alias="element_type")

    @property
    def icon(self) -> str:
        return (
            f"https://act-webstatic.hoyoverse.com/game_record/zzz/role_square_avatar/role_square_avatar_{self.id}.png"
        )


class ShiyuDefenseBuff(APIModel):
    """Shiyu Defense buff model."""

    title: str
    text: str


class ShiyuDefenseMonster(APIModel):
    """Shiyu Defense monster model."""

    id: int
    name: str
    weakness: ZZZElementType = pydantic.Field(alias="weak_element_type")
    level: int


class ShiyuDefenseNode(APIModel):
    """Shiyu Defense node model."""

    characters: typing.List[ShiyuDefenseCharacter] = pydantic.Field(alias="avatars")
    bangboo: ShiyuDefenseBangboo = pydantic.Field(alias="buddy")
    recommended_elements: typing.List[ZZZElementType] = pydantic.Field(alias="element_type_list")
    enemies: typing.List[ShiyuDefenseMonster] = pydantic.Field(alias="monster_info")

    @pydantic.field_validator("enemies", mode="before")
    @classmethod
    def __convert_enemies(
        cls, value: typing.Dict[typing.Literal["level", "list"], typing.Any]
    ) -> typing.List[ShiyuDefenseMonster]:
        level = value["level"]
        result: typing.List[ShiyuDefenseMonster] = []
        for monster in value["list"]:
            monster["level"] = level
            result.append(ShiyuDefenseMonster(**monster))
        return result


class ShiyuDefenseFloor(APIModel):
    """Shiyu Defense floor model."""

    index: int = pydantic.Field(alias="layer_index")
    rating: typing.Literal["S", "A", "B"]
    id: int = pydantic.Field(alias="layer_id")
    buffs: typing.List[ShiyuDefenseBuff]
    node_1: ShiyuDefenseNode
    node_2: ShiyuDefenseNode
    challenge_time: datetime.datetime = pydantic.Field(alias="floor_challenge_time")
    name: str = pydantic.Field(alias="zone_name")

    @pydantic.field_validator("challenge_time", mode="before")
    @classmethod
    def __add_timezone(
        cls, v: typing.Dict[typing.Literal["year", "month", "day", "hour", "minute", "second"], int]
    ) -> datetime.datetime:
        return datetime.datetime(
            v["year"], v["month"], v["day"], v["hour"], v["minute"], v["second"], tzinfo=CN_TIMEZONE
        )


class ShiyuDefense(APIModel):
    """ZZZ Shiyu Defense model."""

    schedule_id: int
    begin_time: typing.Optional[datetime.datetime] = pydantic.Field(alias="hadal_begin_time")
    end_time: typing.Optional[datetime.datetime] = pydantic.Field(alias="hadal_end_time")
    has_data: bool
    ratings: typing.Mapping[typing.Literal["S", "A", "B"], int] = pydantic.Field(alias="rating_list")
    floors: typing.List[ShiyuDefenseFloor] = pydantic.Field(alias="all_floor_detail")
    fastest_clear_time: int = pydantic.Field(alias="fast_layer_time")
    """Fastest clear time this season in seconds."""
    max_floor: int = pydantic.Field(alias="max_layer")

    @pydantic.field_validator("ratings", mode="before")
    @classmethod
    def __convert_ratings(
        cls, v: typing.List[typing.Dict[typing.Literal["times", "rating"], typing.Any]]
    ) -> typing.Mapping[typing.Literal["S", "A", "B"], int]:
        return {d["rating"]: d["times"] for d in v}

    @pydantic.field_validator("begin_time", "end_time", mode="before")
    @classmethod
    def __add_timezone(
        cls, v: typing.Optional[typing.Dict[typing.Literal["year", "month", "day", "hour", "minute", "second"], int]]
    ) -> typing.Optional[datetime.datetime]:
        if v is not None:
            return datetime.datetime(
                v["year"], v["month"], v["day"], v["hour"], v["minute"], v["second"], tzinfo=CN_TIMEZONE
            )
        return None
