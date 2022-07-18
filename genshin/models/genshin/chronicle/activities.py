"""Chronicle activities models."""
import datetime
import re
import typing

import pydantic
import pydantic.generics

from genshin.models.genshin import character
from genshin.models.model import Aliased, APIModel

__all__ = [
    "Activities",
    "Activity",
    "EnergyAmplifier",
    "HyakuninIkki",
    "LabyrinthWarriors",
    "OldActivity",
    "Potion",
    "Summer",
]

ModelT = typing.TypeVar("ModelT", bound=APIModel)


class OldActivity(APIModel, pydantic.generics.GenericModel, typing.Generic[ModelT]):
    """Arbitrary activity for chinese events."""

    # sometimes __parameters__ may not be provided in older versions
    __parameters__: typing.ClassVar[typing.Tuple[typing.Any, ...]] = (ModelT,)  # type: ignore

    exists_data: bool
    records: typing.Sequence[ModelT]


class Activity(OldActivity[ModelT]):
    """Arbitrary activity for chinese events."""

    start_time: datetime.datetime
    end_time: datetime.datetime
    total_score: int

    # cn only
    total_times: int = 1


# ---------------------------------------------------------
# Summer：


class SummerStoryRecord(APIModel):
    """Summer story record."""

    finish_time: typing.Optional[datetime.datetime]
    finished: bool
    icon: str
    name: str

    @pydantic.validator("finish_time", pre=True)
    def __validate_time(cls, value: typing.Any) -> datetime.datetime:
        if value is None:
            return None  # type: ignore
        if isinstance(value, datetime.datetime):
            return value

        return datetime.datetime(value["year"], value["month"], value["day"], value["hour"], value["minute"])


class SummerStory(APIModel):
    """Summer story."""

    records: typing.Sequence[SummerStoryRecord] = Aliased("records")


class SummerSailingRecord(APIModel):
    """Summer sailing record."""

    cost_time: int
    finished: bool
    id: int


class SummerSailing(APIModel):
    """Summer Sailing."""

    records: typing.Sequence[SummerSailingRecord] = Aliased("records")


class SummerChallengeRecord(APIModel):
    """Summer challenge record."""

    id: int
    finish_time: typing.Optional[datetime.datetime] = Aliased(None, "finish_time")
    finished: bool
    success: int = Aliased("success_num")
    skill_use: int = Aliased("skill_use_num")
    name: str
    icon: str

    @pydantic.validator("finish_time", pre=True)
    def __validate_time(cls, value: typing.Any) -> datetime.datetime:
        if value is None:
            return None  # type: ignore
        if isinstance(value, datetime.datetime):
            return value

        return datetime.datetime(value["year"], value["month"], value["day"], value["hour"], value["minute"])


class SummerChallenge(APIModel):
    """Summer challenge."""

    records: typing.Sequence[SummerChallengeRecord] = Aliased("records")


class Summer(APIModel):
    """Summer event."""

    anchor: int = Aliased("anchor_number")
    chest: int = Aliased("chest_number")
    way_point: int = Aliased("way_point_number")
    sailing: typing.Optional[SummerSailing] = Aliased(None, "sailing")
    story: typing.Optional[SummerStory] = Aliased(None, "story")
    challenge: typing.Optional[SummerChallenge] = Aliased(None, "challenge")


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


class HyakuninIkki(APIModel):
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


class LabyrinthWarriors(APIModel):
    """Labyrinth Warriors challenge."""

    id: int = Aliased("challenge_id")
    name: str = Aliased("challenge_name")
    passed: bool = Aliased("is_passed")
    level: int = Aliased("settled_level")

    main_characters: typing.Sequence[LabyrinthWarriorsCharacter] = Aliased("main_avatars")
    support_characters: typing.Sequence[LabyrinthWarriorsCharacter] = Aliased("support_avatars")
    runes: typing.Sequence[LabyrinthWarriorsRune]


# ---------------------------------------------------------
# Energy Amplifier Fruition:


class EnergyAmplifierCharacter(character.BaseCharacter):
    """Energy Amplifier character."""

    level: int


class EnergyAmplifierCriteria(APIModel):
    """Energy Amplifier criteria."""

    id: int
    description: str = Aliased("desc")
    score: int


class EnergyAmplifierBuff(APIModel):
    """Energy Amplifier buff."""

    id: int
    name: str
    quality: int
    description: str = Aliased("desc")
    energy: int


class EnergyAmplifier(APIModel):
    """Energy Amplifier challenge."""

    id: int = Aliased("challenge_id")
    name: str = Aliased("challenge_name")
    energy: int
    difficulty: int
    max_score: int
    score_multiplier: int = Aliased("score_multiple")

    characters: typing.Sequence[EnergyAmplifierCharacter] = Aliased("avatars")
    criteria: typing.Sequence[EnergyAmplifierCriteria] = Aliased("limit_conditions")
    buffs: typing.Sequence[EnergyAmplifierBuff]


# ---------------------------------------------------------
# A Study In Potions:


class PotionCharacter(APIModel):
    """Study In Potions character."""

    level: int
    trial: bool = Aliased("is_trial")


class PotionBuff(APIModel):
    """Study In Potions buff."""

    id: int
    name: str
    description: str = Aliased("desc")
    quality: int
    icon: str
    mark: str = Aliased("cornor_mark")


class PotionStage(APIModel):
    """Study In Potions stage."""

    name: str = Aliased("level_name")
    difficulty: int
    difficulty_id: int
    score: int
    score_multiplier: int = Aliased("factor")

    characters: typing.Sequence[PotionCharacter] = Aliased("avatars")
    buffs: typing.Sequence[PotionBuff]


class Potion(APIModel):
    """Study In Potions challenge."""

    name: str = Aliased("stage_name")
    score: int = Aliased("stage_score")
    finished: bool
    stages: typing.Sequence[PotionStage] = Aliased("levels")


# ---------------------------------------------------------
# Activities:


class Activities(APIModel):
    """Collection of genshin activities."""

    hyakunin_ikki_v21: typing.Optional[OldActivity[HyakuninIkki]] = pydantic.Field(None, gslug="sumo")
    hyakunin_ikki_v25: typing.Optional[OldActivity[HyakuninIkki]] = pydantic.Field(None, gslug="sumo_second")
    labyrinth_warriors: typing.Optional[OldActivity[LabyrinthWarriors]] = pydantic.Field(None, gslug="rogue")
    energy_amplifier: typing.Optional[Activity[EnergyAmplifier]] = pydantic.Field(None, gslug="channeller_slab_copy")
    study_in_potions: typing.Optional[OldActivity[Potion]] = pydantic.Field(None, gslug="potion")
    summer: typing.Optional[Summer] = pydantic.Field(None, gslug="summer_v2")

    effigy: typing.Optional[Activity[typing.Any]] = None
    mechanicus: typing.Optional[Activity[typing.Any]] = None
    fleur_fair: typing.Optional[Activity[typing.Any]] = None
    channeller_slab: typing.Optional[Activity[typing.Any]] = None
    martial_legend: typing.Optional[Activity[typing.Any]] = None
    chess: typing.Optional[Activity[typing.Any]] = None

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
