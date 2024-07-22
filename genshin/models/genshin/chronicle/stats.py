from __future__ import annotations

import re
import typing

if typing.TYPE_CHECKING:
    import pydantic.v1 as pydantic
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
        import pydantic

from genshin.models import hoyolab
from genshin.models.model import Aliased, APIModel

from . import abyss, activities, characters

__all__ = [
    "AreaExploration",
    "BossKill",
    "Exploration",
    "FullGenshinUserStats",
    "GenshinUserStats",
    "Offering",
    "PartialGenshinUserStats",
    "Stats",
    "Teapot",
    "TeapotRealm",
]


# flake8: noqa: E222
class Stats(APIModel):
    """Overall user stats."""

    # This is such fucking bullshit, just why?
    # fmt: off
    achievements: int =       Aliased("achievement_number",     mi18n="bbs/achievement_complete_count")
    days_active: int =        Aliased("active_day_number",      mi18n="bbs/active_day")
    characters: int =         Aliased("avatar_number",          mi18n="bbs/other_people_character")
    spiral_abyss: str =       Aliased("spiral_abyss",           mi18n="bbs/unlock_portal")
    anemoculi: int =          Aliased("anemoculus_number",      mi18n="bbs/wind_god")
    geoculi: int =            Aliased("geoculus_number",        mi18n="bbs/rock_god")
    dendroculi: int =         Aliased("dendroculus_number",     mi18n="bbs/dendro_culus")
    electroculi: int =        Aliased("electroculus_number",    mi18n="bbs/electroculus_god")
    hydroculi: int =          Aliased("hydroculus_number",      mi18n="bbs/hydro_god")
    common_chests: int =      Aliased("common_chest_number",    mi18n="bbs/general_treasure_box_count")
    exquisite_chests: int =   Aliased("exquisite_chest_number", mi18n="bbs/delicacy_treasure_box_count")
    precious_chests: int =    Aliased("precious_chest_number",  mi18n="bbs/rarity_treasure_box_count")
    luxurious_chests: int =   Aliased("luxurious_chest_number", mi18n="bbs/magnificent_treasure_box_count")
    remarkable_chests: int =  Aliased("magic_chest_number",     mi18n="bbs/magic_chest_number")
    unlocked_waypoints: int = Aliased("way_point_number",       mi18n="bbs/unlock_portal")
    unlocked_domains: int =   Aliased("domain_number",          mi18n="bbs/unlock_secret_area")
    # fmt: on

    def as_dict(self, lang: typing.Optional[str] = None) -> typing.Mapping[str, typing.Any]:
        """Turn fields into properly named ones."""
        return {
            self._get_mi18n(field, lang or self.lang): getattr(self, field.name)
            for field in self.__fields__.values()
            if field.name != "lang"
        }


class Offering(APIModel):
    """Exploration offering."""

    name: str
    level: int
    icon: str = ""


class BossKill(APIModel):
    """Boss kills in exploration"""

    name: str
    kills: int = Aliased("kill_num")


class AreaExploration(APIModel):
    """Area exploration data."""

    name: str
    raw_explored: int = Aliased("exploration_percentage")


class Exploration(APIModel):
    """Exploration data."""

    id: int
    parent_id: int
    name: str
    raw_explored: int = Aliased("exploration_percentage")

    # deprecated in a sense:
    type: str
    level: int

    icon: str
    inner_icon: str
    background_image: str
    cover: str
    map_url: str

    offerings: typing.Sequence[Offering]
    boss_list: typing.Sequence[BossKill]
    area_exploration_list: typing.Sequence[AreaExploration]

    @property
    def explored(self) -> float:
        """The percentage explored."""
        return self.raw_explored / 10

    @pydantic.validator("offerings", pre=True)
    def __add_base_offering(
        cls,
        offerings: typing.Sequence[typing.Any],
        values: typing.Dict[str, typing.Any],
    ) -> typing.Sequence[typing.Any]:
        if values["type"] == "Reputation" and not any(values["type"] == o["name"] for o in offerings):
            offerings = [*offerings, dict(name=values["type"], level=values["level"])]

        return offerings

    @pydantic.validator("boss_list", pre=True)
    def _add_base_boss_list(
        cls,
        boss_list: typing.Sequence[typing.Any],
    ):
        if not boss_list:
            return []
        return [BossKill(**boss) for boss in boss_list]

    @pydantic.validator("area_exploration_list", pre=True)
    def _add_base_area_exploration_list(
        cls,
        area_exploration_list: typing.Sequence[typing.Any],
    ):
        if not area_exploration_list:
            return []
        return [AreaExploration(**area) for area in area_exploration_list]


class TeapotRealm(APIModel):
    """A specific teapot realm."""

    name: str
    icon: str

    @property
    def id(self) -> int:
        match = re.search(r"\d", self.icon)
        return int(match.group()) if match else 0


class Teapot(APIModel):
    """User's Serenitea Teapot."""

    realms: typing.Sequence[TeapotRealm]
    level: int
    visitors: int = Aliased("visit_num")
    comfort: int = Aliased("comfort_num")
    items: int = Aliased("item_num")
    comfort_name: str = Aliased("comfort_level_name")
    comfort_icon: str = Aliased("comfort_level_icon")


class PartialGenshinUserStats(APIModel):
    """User stats with characters without equipment."""

    info: hoyolab.UserInfo = Aliased("role")
    stats: Stats
    characters: typing.Sequence[characters.PartialCharacter] = Aliased("avatars")
    explorations: typing.Sequence[Exploration] = Aliased("world_explorations")
    teapot: typing.Optional[Teapot] = Aliased("homes")

    @pydantic.validator("teapot", pre=True)
    def __format_teapot(cls, v: typing.Any) -> typing.Optional[typing.Dict[str, typing.Any]]:
        if not v:
            return None
        if isinstance(v, dict):
            return typing.cast("dict[str, typing.Any]", v)
        return {**v[0], "realms": v}


class GenshinUserStats(PartialGenshinUserStats):
    """User stats with characters with equipment"""

    characters: typing.Sequence[characters.Character] = Aliased("avatars")


class FullGenshinUserStats(GenshinUserStats):
    """User stats with all data a user can have"""

    abyss: abyss.SpiralAbyssPair
    activities: activities.Activities
