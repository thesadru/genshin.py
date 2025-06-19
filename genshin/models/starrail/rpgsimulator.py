"""HSR Lineup Simulator."""

import datetime
import typing
from enum import Enum

import pydantic

from genshin.models.model import Aliased, APIModel, DateTime

from . import character

__all__ = (
    "APCShadowLineup",
    "APCShadowLineupResponse",
    "APCShadowSchedule",
    "LineupDetail",
    "MOCSchedule",
    "PureFictionLineup",
    "PureFictionLineupResponse",
    "PureFictionSchedule",
    "StarRailGameMode",
    "StarRailGameModeBuff",
    "StarRailGameModeFloor",
    "StarRailGameModeSchedule",
    "StarRailGameModeType",
    "StarRailLineup",
    "StarRailLineupPlayer",
    "StarRailLineupResponse",
)


class StarRailGameModeType(str, Enum):
    """HSR lineup game mode enum."""

    MOC = "Chasm"
    """Memory of Chaos."""
    PURE_FICTION = "Story"
    """Pure Fiction."""
    APC_SHADOW = "Boss"
    """Apocalyptic Shadow."""


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
    floors: typing.Sequence[StarRailGameModeFloor]
    type: StarRailGameModeType = Aliased("root_type")

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
    start_time: datetime.datetime = Aliased("schedule_begin_time")
    end_time: datetime.datetime = Aliased("schedule_end_time")

    is_now: bool
    is_show: bool
    floor_nums: int


class APCShadowSchedule(StarRailGameModeSchedule):
    """Apocalyptic Shadow schedule."""

    buff: StarRailGameModeBuff
    node1_buffs: typing.Sequence[StarRailGameModeBuff] = Aliased("addition_buff_1")
    node2_buffs: typing.Sequence[StarRailGameModeBuff] = Aliased("addition_buff_2")

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

    buffs: typing.Sequence[StarRailGameModeBuff] = Aliased("addition_buff")
    default_buffs: typing.Sequence[StarRailGameModeBuff] = Aliased("sub_maze_buff_list")


class StarRailLineupPlayer(APIModel):
    """A HSR lineup player."""

    uid: str
    nickname: str
    avatar_url: str
    level: int


class StarRailLineup(APIModel):
    """A HSR lineup."""

    id: str
    player: StarRailLineupPlayer
    type: StarRailGameModeType = Aliased("lineup_type")

    title: str
    description: str
    likes: int = Aliased("like_cnt")
    comments: int = Aliased("comment_cnt")
    favorites: int = Aliased("favour_cnt")
    views: int = Aliased("view_cnt")

    created_at: datetime.datetime
    last_edited_at: datetime.datetime = Aliased("last_edit")

    stars: int = Aliased("star_num")
    cycles_taken: int = Aliased("round_num")

    characters: typing.Sequence[typing.Sequence[character.StarRailLineupCharacter]] = Aliased("avatar_group")

    @pydantic.field_validator("characters", mode="before")
    @classmethod
    def __unnest_characters(
        cls, v: typing.Sequence[dict[str, typing.Any]]
    ) -> typing.Sequence[typing.Sequence[dict[str, typing.Any]]]:
        # Merge relic info from "group"
        for g in v:
            group = g["group"]

            for avatar in g["avatar_details"]:
                group_avatar = next((a for a in group if a["item_id"] == str(avatar["id"])), None)
                if not group_avatar:
                    continue

                relics = group_avatar.get("relics", []) + group_avatar.get("relic_sides", [])

                for relic in avatar.get("relics", []):
                    group_avatar_relic = next((r for r in relics if r["item_id"] == str(relic["id"])), None)
                    if not group_avatar_relic:
                        continue

                    relic.update(group_avatar_relic)

        return [g["avatar_details"] for g in v]

    @pydantic.model_validator(mode="before")
    @classmethod
    def __nest_player(cls, v: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Nest the player field."""
        v["player"] = {
            "uid": v["account_uid"],
            "nickname": v["nickname"],
            "avatar_url": v["avatar_url"],
            "level": v["game_level"],
        }
        return v


class LineupDetail(APIModel):
    """Detail for a lineup."""

    buffs: typing.Sequence[StarRailGameModeBuff] = Aliased("buff_list")
    points: int


class PureFictionLineup(StarRailLineup):
    """A Pure Fiction lineup."""

    detail: LineupDetail = Aliased("story_info")
    node1_challenged_at: DateTime = Aliased("challenge_time")
    node2_challenged_at: DateTime = Aliased("challenge_time_node2")


class APCShadowLineup(StarRailLineup):
    """A Apocalyptic Shadow lineup."""

    detail: LineupDetail = Aliased("boss_info")
    node1_challenged_at: DateTime = Aliased("challenge_time")
    node2_challenged_at: DateTime = Aliased("challenge_time_node2")


class StarRailLineupResponse(APIModel):
    """Response for HSR lineups."""

    lineups: typing.Sequence[StarRailLineup] = Aliased("list")
    next_page_token: str


class PureFictionLineupResponse(APIModel):
    """Response for Pure Fiction lineups."""

    lineups: typing.Sequence[PureFictionLineup] = Aliased("list")
    next_page_token: str


class APCShadowLineupResponse(APIModel):
    """Response for Apocalyptic Shadow lineups."""

    lineups: typing.Sequence[APCShadowLineup] = Aliased("list")
    next_page_token: str
