"""ZZZ data overview models."""

import typing

import pydantic

from genshin.models.model import Aliased, APIModel

from ..character import ZZZPartialAgent

__all__ = ("HIACoin", "ZZZBaseBangboo", "ZZZCatNote", "ZZZGameData", "ZZZMedal", "ZZZStats", "ZZZUserStats")


class HIACoin(APIModel):
    """HIACoin model."""

    num: int
    name: str
    icon: str = Aliased("url")


class ZZZStats(APIModel):
    """ZZZ data overview stats."""

    active_days: int
    character_num: int = Aliased("avatar_num")
    inter_knot_reputation: str = Aliased("world_level_name")
    shiyu_defense_frontiers: int = Aliased("cur_period_zone_layer_count")
    bangboo_obtained: int = Aliased("buddy_num")
    achievement_count: int
    hia_coin: typing.Optional[HIACoin] = Aliased("commemorative_coins_list")

    @pydantic.field_validator("hia_coin", mode="before")
    def __unnest_hia_coin(
        cls, v: typing.List[typing.Dict[str, typing.Any]]
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return v[0] if v else None


class ZZZCatNote(APIModel):
    """ZZZ Cat note model."""

    icon: str
    id: int
    is_lock: bool
    name: str
    num: int
    total: int


class ZZZMedal(APIModel):
    """ZZZ player medal model."""

    icon: str = Aliased("medal_icon")
    number: int
    id: int = Aliased("medal_id")
    type: str = Aliased("medal_type")
    name: str
    is_show: bool


class ZZZGameData(APIModel):
    """ZZZ game data model."""

    personal_title: str
    title_main_color: str
    title_bottom_color: str
    title_bg_url: str
    medal_icons: typing.Sequence[str] = Aliased("medal_list")
    card_url: str
    medals: typing.Sequence[ZZZMedal] = Aliased("all_medal_list")


class ZZZBaseBangboo(APIModel):
    """Base bangboo (buddy) model."""

    id: int
    name: str
    rarity: typing.Literal["S", "A"]
    level: int
    star: int
    icon: str = pydantic.Field(
        validation_alias=pydantic.aliases.AliasChoices("bangboo_square_url", "bangboo_rectangle_url")
    )


class ZZZUserStats(APIModel):
    """Zenless Zone Zero user model."""

    stats: ZZZStats
    agents: typing.Sequence[ZZZPartialAgent] = Aliased("avatar_list")
    bangboos: typing.Sequence[ZZZBaseBangboo] = Aliased("buddy_list")
    in_game_avatar: str = Aliased("cur_head_icon_url")
    cat_notes: typing.Sequence[ZZZCatNote] = Aliased("cat_notes_list")
    in_game_data: ZZZGameData = Aliased("game_data_show")
