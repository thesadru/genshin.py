import typing
from enum import Enum

import pydantic

from genshin.models.model import APIModel, TZDateTime, prevent_enum_error

__all__ = (
    "ChallengeStatus",
    "ChallengeType",
    "EventWarp",
    "EventWarpCharacter",
    "EventWarpLightCone",
    "HSRBaseEventItem",
    "HSRChallenge",
    "HSREvent",
    "HSREventCalendar",
    "HSREventReward",
    "HSREventStatus",
    "HSREventTimeType",
    "HSREventType",
    "TimeInfo",
)


class HSREventType(Enum):
    """Event type enum."""

    SIGN_IN = "ActivityTypeSign"
    """Daily sign-in event."""
    OTHER = "ActivityTypeOther"
    DOUBLE_REWARDS = "ActivityTypeDouble"
    """Plannar Fissure, Garden of Plenty, etc."""


class HSREventStatus(Enum):
    """Event status enum."""

    OTHER_LOCKED = "OtherActStatusUnopened"
    OTHER_IN_PROGRESS = "OtherActStatusUnFinish"
    DOUBLE_REWARDS_LOCKED = "DoubleActStatusUnopened"
    SIGN_IN_UNCLAIMED = "SignActStatusUnclaimed"


class HSREventTimeType(Enum):
    """Event time type enum."""

    LONG = "ActTimeTypeLong"
    """Simulated universe."""
    DEFAULT = "ActTimeTypeDefault"


class ChallengeType(Enum):
    """Challenge type enum."""

    APC_SHADOW = "ChallengeTypeBoss"
    """Apocalyptic shadow."""
    MOC = "ChallengeTypeChasm"
    """Memory of Chaos."""
    PURE_FICTION = "ChallengeTypeStory"


class ChallengeStatus(Enum):
    """Challenge status enum."""

    IN_PROGRESS = "challengeStatusInProgress"
    LOCKED = "challengeStatusUnopened"


class TimeInfo(APIModel):
    """Time info model."""

    start: TZDateTime = pydantic.Field(alias="start_ts")
    end: TZDateTime = pydantic.Field(alias="end_ts")
    now: TZDateTime


class HSRBaseEvent(APIModel):
    """HSR base event model."""

    time_info: typing.Optional[TimeInfo] = None

    @pydantic.field_validator("time_info", mode="before")
    def __validate_time_info(cls, v: dict[str, typing.Any]) -> typing.Optional[dict[str, typing.Any]]:
        if not v["start_time"]:
            return None
        return v


class HSRBaseEventItem(APIModel):
    """Base event item model."""

    id: int = pydantic.Field(alias="item_id")
    name: str = pydantic.Field(alias="item_name")
    icon: str = pydantic.Field(alias="icon_url")
    path: int = pydantic.Field(alias="avatar_base_type")

    rarity: int
    wiki_url: str

    is_forward: bool  # No clue what this is


class EventWarpCharacter(HSRBaseEventItem):
    """Event warp character model."""

    icon: str = pydantic.Field(alias="icon_url")
    large_icon: str = pydantic.Field(alias="item_avatar_icon_path")
    element: int = pydantic.Field(alias="damage_type")


class EventWarpLightCone(HSRBaseEventItem):
    """Event warp light cone model."""

    icon: str = pydantic.Field(alias="item_url")


class EventWarp(HSRBaseEvent):
    """Event warp model."""

    name: str
    type: str  # Seems to always be 'CardPoolRole'
    characters: typing.Sequence[EventWarpCharacter] = pydantic.Field(alias="avatar_list")
    light_cones: typing.Sequence[EventWarpLightCone] = pydantic.Field(alias="equip_list")

    is_after_version: bool
    """Whether the event happens after last version's update."""
    version: str
    id: int


class HSREventReward(APIModel):
    """HSR event reward model."""

    id: int = pydantic.Field(alias="item_id")
    name: str
    icon: str
    wiki_url: str
    num: int
    rarity: int


class HSREvent(HSRBaseEvent):
    """HSR event model."""

    id: int
    version: str
    name: str
    description: str = pydantic.Field(alias="panel_desc")

    type: typing.Union[HSREventType, str] = pydantic.Field(alias="act_type")
    time_type: typing.Union[HSREventTimeType, str] = pydantic.Field(alias="act_time_type")
    status: typing.Union[HSREventStatus, str] = pydantic.Field(alias="act_status")

    rewards: typing.Sequence[HSREventReward] = pydantic.Field(alias="reward_list")
    total_progress: int
    current_progress: int
    special_reward: typing.Optional[HSREventReward]

    is_after_version: bool
    """Whether the event happens after last version's update."""
    all_finished: bool
    show_text: str

    # No clue what these are
    strategy: str
    multiple_drop_type: int
    multiple_drop_type_list: list[int]
    count_refresh_type: int
    count_value: int
    drop_multiple: int
    panel_id: int
    sort_weight: int

    @pydantic.field_validator("special_reward", mode="after")
    def __validate_special_reward(cls, v: HSREventReward) -> typing.Optional[HSREventReward]:
        if v.id == 0:
            return None
        return v

    @pydantic.field_validator("type", mode="before")
    def __validate_type(cls, v: str) -> typing.Union[HSREventType, str]:
        return prevent_enum_error(v, HSREventType)

    @pydantic.field_validator("time_type", mode="before")
    def __validate_time_type(cls, v: str) -> typing.Union[HSREventTimeType, str]:
        return prevent_enum_error(v, HSREventTimeType)

    @pydantic.field_validator("status", mode="before")
    def __validate_status(cls, v: str) -> typing.Union[HSREventStatus, str]:
        return prevent_enum_error(v, HSREventStatus)

    @pydantic.field_validator("name", mode="after")
    def __format_name(cls, v: str) -> str:
        return v.replace("\\n", " ")

    @pydantic.field_validator("description", mode="after")
    def __format_description(cls, v: str) -> str:
        return v.replace("\\n", "\n")


class HSRChallenge(HSRBaseEvent):
    """HSR challenge model."""

    id: int = pydantic.Field(alias="group_id")
    name: str = pydantic.Field(alias="name_mi18n")

    type: typing.Union[ChallengeType, str] = pydantic.Field(alias="challenge_type")
    status: typing.Union[ChallengeStatus, str]

    rewards: typing.Sequence[HSREventReward] = pydantic.Field(alias="reward_list")
    special_reward: typing.Optional[HSREventReward]
    total_progress: int
    current_progress: int
    show_text: str

    @pydantic.field_validator("special_reward", mode="after")
    def __validate_special_reward(cls, v: HSREventReward) -> typing.Optional[HSREventReward]:
        if v.id == 0:
            return None
        return v

    @pydantic.field_validator("type", mode="before")
    def __validate_type(cls, v: str) -> typing.Union[ChallengeType, str]:
        return prevent_enum_error(v, ChallengeType)

    @pydantic.field_validator("status", mode="before")
    def __validate_status(cls, v: str) -> typing.Union[ChallengeStatus, str]:
        return prevent_enum_error(v, ChallengeStatus)


class HSREventCalendar(APIModel):
    """HSR event calendar model."""

    character_warps: typing.Sequence[EventWarp] = pydantic.Field(alias="avatar_card_pool_list")
    light_cone_warps: typing.Sequence[EventWarp] = pydantic.Field(alias="equip_card_pool_list")
    events: typing.Sequence[HSREvent] = pydantic.Field(alias="act_list")
    challenges: typing.Sequence[HSRChallenge] = pydantic.Field(alias="challenge_list")

    cur_game_version: str
    """Current game version."""
    now: TZDateTime
