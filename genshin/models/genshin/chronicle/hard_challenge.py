"""Stygian Onslaught models."""

import enum
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, DateTime, LevelField

__all__ = (
    "HardChallenge",
    "HardChallengeBestCharacter",
    "HardChallengeBestCharacterType",
    "HardChallengeBestRecord",
    "HardChallengeCharacter",
    "HardChallengeEnemy",
    "HardChallengeEnemyTag",
    "HardChallengeData",
    "HardChallengeChallenge",
    "HardChallengeSeason",
    "HardChallengeTagElement",
    "HardChallengeTagType",
)


class HardChallengeBestCharacterType(enum.IntEnum):
    """Type of best character in Stygian Onslaught."""

    STRIKE = 1
    """Strongest single strike."""
    DAMAGE = 2
    """Highest total damage dealt."""


class HardChallengeTagType(enum.IntEnum):
    """Type of tag in Stygian Onslaught."""

    DISADVANTAGE = 0
    ADVANTAGE = 1


class HardChallengeTagElement(enum.Enum):
    """Element of tag in Stygian Onslaught."""

    CRYO = "{SPRITE_PRESET#11001}"
    HYDRO = "{SPRITE_PRESET#11002}"
    PYRO = "{SPRITE_PRESET#11003}"
    DENDRO = "{SPRITE_PRESET#11007}"


class HardChallengeSeason(APIModel):
    """A season of Stygian Onslaught."""

    id: int = Aliased("schedule_id")
    name: str
    start_at: DateTime = Aliased("start_date_time")
    end_at: DateTime = Aliased("end_date_time")


class HardChallengeBestRecord(APIModel):
    """Best record for a Stygian Onslaught season."""

    difficulty: int
    time_used: int = Aliased("second")
    """Time used for challenge in seconds."""
    icon: str
    """Badge icon filename."""

    @pydantic.field_validator("icon")
    @classmethod
    def __parse_icon(cls, v: str) -> str:
        return v.split(",")[-1]

class HardChallengeCharacter(APIModel):
    """A character in Stygian Onslaught."""

    id: int = Aliased("avatar_id")
    name: str
    element: str
    icon: str = Aliased("image")
    level: LevelField
    rarity: int
    constellation: int = Aliased("rank")


class HardChallengeBestCharacter(APIModel):
    """Best character in Stygian Onslaught."""

    id: int = Aliased("avatar_id")
    side_icon: str
    value: str = Aliased("dps")
    type: HardChallengeBestCharacterType


class HardChallengeEnemyTag(APIModel):
    """An enemy tag in Stygian Onslaught."""

    type: HardChallengeTagType
    elements: list[HardChallengeTagElement]

    @pydantic.model_validator(mode="before")
    @classmethod
    def __parse_elements(cls, v: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Parse elements from string to HardChallengeTagElement enum."""
        desc = v.get("desc", "")
        for element in HardChallengeTagElement:
            if element.value in desc:
                v.setdefault("elements", []).append(element)
        return v


class HardChallengeEnemy(APIModel):
    """An enemy in Stygian Onslaught."""

    id: int = Aliased("monster_id")
    name: str
    level: LevelField
    icon: str
    descriptions: list[str] = Aliased("desc")
    tags: list[HardChallengeEnemyTag]


class HardChallengeChallenge(APIModel):
    """A single/multi player challenge in Stygian Onslaught."""

    name: str
    time_used: int = Aliased("second")
    """Time used for challenge in seconds."""
    team: list[HardChallengeCharacter] = Aliased("teams")
    best_characters: list[HardChallengeBestCharacter] = Aliased("best_avatar")
    enemy: HardChallengeEnemy = Aliased("monster")


class HardChallengeData(APIModel):
    """Stygian Onslaught single/multi player data."""

    best_record: typing.Optional[HardChallengeBestRecord] = Aliased("best")
    challenges: list[HardChallengeChallenge] = Aliased("challenge")
    has_data: bool


class HardChallenge(APIModel):
    """Stygian Onslaught data."""

    season: HardChallengeSeason = Aliased("schedule")
    single_player: HardChallengeData = Aliased("single")
    multi_player: HardChallengeData = Aliased("mp")
