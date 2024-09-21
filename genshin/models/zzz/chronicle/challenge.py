import datetime
import typing

from genshin.constants import CN_TIMEZONE
from genshin.models.model import Aliased, APIModel
from genshin.models.zzz.character import ZZZElementType

if typing.TYPE_CHECKING:
    import pydantic.v1 as pydantic
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
        import pydantic

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
    element: ZZZElementType = Aliased("element_type")

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
    weakness: typing.Union[ZZZElementType, int] = Aliased("weak_element_type")
    level: int

    @pydantic.validator("weakness", pre=True)
    def __convert_weakness(cls, v: int) -> typing.Union[ZZZElementType, int]:
        try:
            return ZZZElementType(v)
        except ValueError:
            return v


class ShiyuDefenseNode(APIModel):
    """Shiyu Defense node model."""

    characters: typing.List[ShiyuDefenseCharacter] = Aliased("avatars")
    bangboo: ShiyuDefenseBangboo = Aliased("buddy")
    recommended_elements: typing.List[ZZZElementType] = Aliased("element_type_list")
    enemies: typing.List[ShiyuDefenseMonster] = Aliased("monster_info")

    @pydantic.validator("enemies", pre=True)
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

    index: int = Aliased("layer_index")
    rating: typing.Literal["S", "A", "B"]
    id: int = Aliased("layer_id")
    buffs: typing.List[ShiyuDefenseBuff]
    node_1: ShiyuDefenseNode
    node_2: ShiyuDefenseNode
    challenge_time: datetime.datetime = Aliased("floor_challenge_time")
    name: str = Aliased("zone_name")

    @pydantic.validator("challenge_time", pre=True)
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
    begin_time: typing.Optional[datetime.datetime] = Aliased("hadal_begin_time")
    end_time: typing.Optional[datetime.datetime] = Aliased("hadal_end_time")
    has_data: bool
    ratings: typing.Mapping[typing.Literal["S", "A", "B"], int] = Aliased("rating_list")
    floors: typing.List[ShiyuDefenseFloor] = Aliased("all_floor_detail")
    fastest_clear_time: int = Aliased("fast_layer_time")
    """Fastest clear time this season in seconds."""
    max_floor: int = Aliased("max_layer")

    @pydantic.validator("ratings", pre=True)
    @classmethod
    def __convert_ratings(
        cls, v: typing.List[typing.Dict[typing.Literal["times", "rating"], typing.Any]]
    ) -> typing.Mapping[typing.Literal["S", "A", "B"], int]:
        return {d["rating"]: d["times"] for d in v}

    @pydantic.validator("begin_time", "end_time", pre=True)
    @classmethod
    def __add_timezone(
        cls, v: typing.Optional[typing.Dict[typing.Literal["year", "month", "day", "hour", "minute", "second"], int]]
    ) -> typing.Optional[datetime.datetime]:
        if v is not None:
            return datetime.datetime(
                v["year"], v["month"], v["day"], v["hour"], v["minute"], v["second"], tzinfo=CN_TIMEZONE
            )
        return None
