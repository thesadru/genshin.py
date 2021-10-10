import re
from typing import List

from pydantic import Field

from .base import BaseCharacter, GenshinModel


class Activity(GenshinModel):
    """A genshin activity"""


class HyakuninIkkiCharacter(BaseCharacter):
    """A possibly trial character"""

    level: int
    trial: bool = Field(galias="is_trail_avatar")


class HyakuninIkkiSkill(GenshinModel):
    """A Hyakunin Ikki skill"""

    id: int
    name: str
    icon: str
    desc: str


class HyakuninIkkiBattle(GenshinModel):
    """A Hyakunin Ikki challenge"""

    characters: List[HyakuninIkkiCharacter] = Field(galias="avatars")
    skills: List[HyakuninIkkiSkill] = Field(galias="skills")


class HyakuninIkkiChallenge(GenshinModel):
    """A Hyakunin Ikki challenge"""

    id: int = Field(galias="challenge_id")
    name: str = Field(galias="challenge_name")
    difficulty: int
    multiplier: int = Field(galias="score_multiple")
    score: int = Field(galias="max_score")
    medal_icon: str = Field(galias="heraldry_icon")

    battles: List[HyakuninIkkiBattle] = Field(galias="lineups")

    @property
    def medal(self) -> str:
        match = re.search(r"heraldry_(\w+)\.png", self.medal_icon)
        return match.group(1) if match else ""


class HyakuninIkki(Activity):
    """A Hyakunin Ikki event"""

    challenges: List[HyakuninIkkiChallenge] = Field(galias="records")


class Activities(GenshinModel):
    """A collection of genshin activities"""

    hyakunin: HyakuninIkki = Field(galias="sumo")
