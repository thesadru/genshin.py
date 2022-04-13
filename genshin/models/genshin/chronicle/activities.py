"""Chronicle activities models."""
import datetime
import re
import typing

import pydantic

from genshin.models.genshin import character
from genshin.models.model import Aliased, APIModel

__all__ = [
    "Activities",
    "ChineseActivity",
    "HyakuninIkki",
    "HyakuninIkkiBattle",
    "HyakuninIkkiChallenge",
    "HyakuninIkkiCharacter",
    "HyakuninIkkiSkill",
    "LabyrinthWarriors",
    "LabyrinthWarriorsChallenge",
    "LabyrinthWarriorsCharacter",
    "LabyrinthWarriorsRune",
]

# ---------------------------------------------------------
# Hyakunin Ikki:


class HyakuninIkkiCharacter(character.BaseCharacter):
    """Possibly trial Hyakunin Ikki character."""

    level: int
    trial: bool = Aliased("is_trail_avatar")


class HyakuninIkkiSkill(APIModel):
    """Hyakunin Ikki skill."""

    id: int
    name: str
    icon: str
    description: str = Aliased("desc")


class HyakuninIkkiBattle(APIModel):
    """Hyakunin Ikki battle."""

    characters: typing.Sequence[HyakuninIkkiCharacter] = Aliased("avatars")
    skills: typing.Sequence[HyakuninIkkiSkill] = Aliased("skills")


class HyakuninIkkiChallenge(APIModel):
    """Hyakunin Ikki challenge."""

    id: int = Aliased("challenge_id")
    name: str = Aliased("challenge_name")
    difficulty: int
    multiplier: int = Aliased("score_multiple")
    score: int = Aliased("max_score")
    medal_icon: str = Aliased("heraldry_icon")

    battles: typing.Sequence[HyakuninIkkiBattle] = Aliased("lineups")

    @property
    def medal(self) -> str:
        match = re.search(r"heraldry_(\w+)\.png", self.medal_icon)
        return match.group(1) if match else ""


class HyakuninIkki(APIModel):
    """Hyakunin Ikki event."""

    challenges: typing.Sequence[HyakuninIkkiChallenge] = Aliased("records")


# ---------------------------------------------------------
# Labyrinth Warriors:


class LabyrinthWarriorsCharacter(character.BaseCharacter):
    """Labyrinth Warriors character."""

    level: int


class LabyrinthWarriorsRune(APIModel):
    """Labyrinth Warriors rune."""

    id: int
    icon: str
    name: str
    description: str = Aliased("desc")
    element: str


class LabyrinthWarriorsChallenge(APIModel):
    """Labyrinth Warriors challenge."""

    id: int = Aliased("challenge_id")
    name: str = Aliased("challenge_name")
    passed: bool = Aliased("is_passed")
    level: int = Aliased("settled_level")

    main_characters: typing.Sequence[LabyrinthWarriorsCharacter] = Aliased("main_avatars")
    support_characters: typing.Sequence[LabyrinthWarriorsCharacter] = Aliased("support_avatars")
    runes: typing.Sequence[LabyrinthWarriorsRune]


class LabyrinthWarriors(APIModel):
    """Labyrinth Warriors event."""

    challenges: typing.Sequence[LabyrinthWarriorsChallenge] = Aliased("records")


# ---------------------------------------------------------
# Chinese activities:


class ChineseActivity(APIModel):
    """Srbitrary activity for chinese events."""

    start_time: datetime.datetime
    end_time: datetime.datetime
    total_score: int
    total_times: int
    records: typing.Sequence[typing.Any]


# ---------------------------------------------------------
# Activities:


class Activities(APIModel):
    """Collection of genshin activities."""

    hyakunin_ikki: typing.Optional[HyakuninIkki] = pydantic.Field(None, gslug="sumo")
    labyrinth_warriors: typing.Optional[LabyrinthWarriors] = pydantic.Field(None, gslug="rogue")

    effigy: typing.Optional[ChineseActivity] = None
    mechanicus: typing.Optional[ChineseActivity] = None
    challenger_slab: typing.Optional[ChineseActivity] = None
    martial_legend: typing.Optional[ChineseActivity] = None
    chess: typing.Optional[ChineseActivity] = None

    @pydantic.root_validator(pre=True)
    def __flatten_activities(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        if not values.get("activities"):
            return values

        slugs = {
            field.field_info.extra["gslug"]: name
            for name, field in cls.__fields__.items()
            if field.field_info.extra.get("gslug")
        }

        for activity in values["activities"]:
            for name, value in activity.items():
                if "exists_data" not in value:
                    continue

                name = slugs.get(name, name)
                values[name] = value if value["exists_data"] else None

        return values
