"""Event calendar models."""

import datetime
import typing

from genshin.models.model import Aliased, APIModel

__all__ = (
    "AbyssDetail",
    "Banner",
    "BannerCharacter",
    "BannerWeapon",
    "DateTime",
    "DoubleRewardDetail",
    "Event",
    "EventExplorationDetail",
    "EventReward",
    "GenshinEventCalendar",
    "TheaterDetail",
)


class BannerCharacter(APIModel):
    """Banner character."""

    id: int
    icon: str
    name: str
    element: str
    rarity: typing.Literal[4, 5]


class BannerWeapon(APIModel):
    """Banner weapon."""

    id: int
    icon: str
    rarity: typing.Literal[4, 5]
    name: str
    wiki_url: str


class DateTime(APIModel):
    """Date time model"""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int

    @property
    def dt(self) -> datetime.datetime:
        return datetime.datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)


class Banner(APIModel):
    """Banner model."""

    id: int = Aliased("pool_id")
    version: str = Aliased("version_name")  # e.g. 5.2
    name: str = Aliased("pool_name")
    type: int = Aliased("pool_type")

    characters: typing.Sequence[BannerCharacter] = Aliased("avatars")
    weapons: typing.Sequence[BannerWeapon] = Aliased("weapon")

    start_timestamp: int
    end_timestamp: int
    start_time: DateTime
    end_time: DateTime

    jump_url: str
    pool_status: int
    countdown_seconds: int


class EventReward(APIModel):
    """Event reward model."""

    id: int = Aliased("item_id")
    name: str
    icon: str
    wiki_url: str
    num: int
    rarity: int
    homepage_show: bool


class EventExplorationDetail(APIModel):
    """Event exploration detail."""

    explored_percentage: float = Aliased("explore_percent")
    is_finished: bool


class DoubleRewardDetail(APIModel):
    """Double reward detail."""

    total: int
    remaining: int = Aliased("left")


class AbyssDetail(APIModel):
    """Spiral abyss detail."""

    unlocked: bool = Aliased("is_unlock")
    max_star: int
    total_star: int
    has_data: bool


class TheaterDetail(APIModel):
    """Imaginarium theater detail."""

    unlocked: bool = Aliased("is_unlock")
    max_round: int = Aliased("max_round_id")
    has_data: bool


class Event(APIModel):
    """Event model."""

    id: int
    name: str
    description: str = Aliased("desc")
    strategy: str
    type: str

    start_timestamp: int
    end_timestamp: int
    start_time: DateTime
    end_time: DateTime

    status: int
    countdown_seconds: int
    rewards: typing.Sequence[EventReward] = Aliased("reward_list")
    is_finished: bool

    exploration_detail: typing.Optional[EventExplorationDetail] = Aliased("explore_detail", default=None)
    double_reward_detail: typing.Optional[DoubleRewardDetail] = Aliased("double_detail", default=None)
    abyss_detail: typing.Optional[AbyssDetail] = Aliased("tower_detail", default=None)
    theater_detail: typing.Optional[TheaterDetail] = Aliased("theater_detail", default=None)


class GenshinEventCalendar(APIModel):
    """Genshin event calendar."""

    character_banners: typing.Sequence[Banner] = Aliased("avatar_card_pool_list")
    weapon_banners: typing.Sequence[Banner] = Aliased("weapon_card_pool_list")
    events: typing.Sequence[Event] = Aliased("act_list")
