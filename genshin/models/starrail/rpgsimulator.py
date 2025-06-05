"""HSR Lineup Simulator."""

import datetime
import typing

import pydantic

from genshin.models.model import APIModel, Aliased
from . import character


class StarRailGameModeFloor(APIModel):
    """A floor of a game mode, like MOC Stage 1."""

    id: int
    name: str
    floor: int

    @pydantic.model_validator(mode="before")
    @classmethod
    def __extract_floor(cls, v: dict[str, typing.Any]) -> dict[str, typing.Any]:
        extend = v["extend"]
        v["floor"] = extend["floor"]
        return v


class StarRailGameMode(APIModel):
    """HSR game mode, like MOC."""

    id: int
    name: str
    floors: list[StarRailGameModeFloor]

    @pydantic.model_validator(mode="before")
    @classmethod
    def __unnest_children(cls, v: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Unnest the children field."""
        if not (children := v.get("children")):
            msg = "Missing 'children' field in HSRGameMode."
            raise ValueError(msg)

        v["floors"] = children[0]["children"]
        v["name"] = children[0]["name"]
        return v


class StarRailGameModeBuff(APIModel):
    """HSR game mode buff."""

    name: str
    desc: str
    icon: typing.Optional[str] = None
    simple_desc: typing.Optional[str] = None


class StarRailGameModeSchedule(APIModel):
    """Base HSR lineup game mode schedule."""

    id: int = Aliased("group_id")
    name: str = Aliased("name_mi18n")
    begin_time: datetime.datetime = Aliased("schedule_begin_time")
    end_time: datetime.datetime = Aliased("schedule_end_time")

    is_now: bool
    is_show: bool
    floor_nums: int


class APCShadowSchedule(StarRailGameModeSchedule):
    """Apocalyptic Shadow schedule."""

    buff: StarRailGameModeBuff
    node_1_small_buffs: list[StarRailGameModeBuff] = Aliased("addition_buff_1")
    node_2_small_buffs: list[StarRailGameModeBuff] = Aliased("addition_buff_2")

    @pydantic.model_validator(mode="before")
    @classmethod
    def __convert_buffs(cls, v: dict[str, typing.Any]) -> dict[str, typing.Any]:
        v["buff"] = {"name": v["maze_buff_name_mi18n"], "desc": v["maze_buff_desc_mi18n"], "icon": v["buff_icon"]}
        return v


class MOCSchedule(StarRailGameModeSchedule):
    """Memory of Chaos schedule."""

    buff: StarRailGameModeBuff

    @pydantic.model_validator(mode="before")
    @classmethod
    def __convert_buffs(cls, v: dict[str, typing.Any]) -> dict[str, typing.Any]:
        v["buff"] = {"name": v["maze_buff_name_mi18n"], "desc": v["maze_buff_desc_mi18n"]}
        return v


class PureFictionSchedule(StarRailGameModeSchedule):
    """Pure Future schedule."""

    buffs: list[StarRailGameModeBuff] = Aliased("addition_buff")
    default_buffs: list[StarRailGameModeBuff] = Aliased("sub_maze_buff_list")


class StarRailLineup(APIModel):
    """A HSR lineup."""

    id: str
    uid: str = Aliased("account_uid")
    nickname: str
    avatar_url: str

    title: str
    characters: list[list[character.StarRailLineupCharacter]] = Aliased("avatar_group")

    @pydantic.field_validator("characters", mode="before")
    @classmethod
    def __unnest_characters(cls, v: list[dict[str, typing.Any]]) -> list[list[dict[str, typing.Any]]]:
        return [g["avatar_details"] for g in v]


class StarRailLineupResponse(APIModel):
    """Response for HSR lineups."""

    lineups: list[StarRailLineup] = Aliased("list")
    next_page_token: str
