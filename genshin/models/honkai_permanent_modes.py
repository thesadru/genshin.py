import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field, root_validator, validator

from .base import GenshinModel, Unique
from .honkai_base import Battlesuit
from ..constants import REMEMBRANCE_SIGILS, RemembranceSigil

__all__ = (
    "Boss",
    "ELF",
    "SuperstringAbyss",
    "MemorialBattle",
    "MemorialArena",
    "ElysianRealm",
)


# GENERIC


class Boss(GenshinModel, Unique):
    id: int
    name: str
    icon: str = Field(galias="avatar")


class ELF(GenshinModel, Unique):

    id: int
    name: str
    icon: str = Field(galias="avatar")
    rarity: str
    upgrade_level: int = Field(galias="star")

    @validator("rarity", pre=True)
    def __fix_rank(cls, rarity: int):
        # ELFs come in rarities A and S, API returns 3 and 4, respectively
        return ["A", "S"][rarity - 3]


# ABYSS

# TODO: Check if other abyss modes return different data.
#       I can't actually do this myself atm as the modes are level gated,
#       and being max level I no longer have access to 2/3 modes.
#       Especially since the entire trophy mechanic is bound to the
#       highest level-bracket of Abyss, I'm inclined to believe this won't
#       work for lower level-brackets.

# Considering the above todo, I've decided to name this class after the
# highest level-bracket abyss mode for now: Superstring Dimension.


class SuperstringAbyss(GenshinModel):
    """Represents one cycle of abyss (3 days per cycle, 2 cycles per week)"""

    score: int
    end_time: datetime = Field(galias="updated_time_second")
    boss: Boss
    lineup: List[Battlesuit]
    elf: ELF

    placement: int = Field(galias="rank")
    trophies_gained: int = Field(galias="settled_cup_number")
    end_trophies: int = Field(galias="cup_number")
    start_rank: str = Field(galias="level")
    end_rank: str = Field(galias="settled_level")

    @validator("start_rank", "end_rank", pre=True)
    def __fix_ranks(cls, rank: int):
        return (
            "Forbidden",
            "Sinful I",
            "Sinful II",
            "Sinful III",
            "Agony I",
            "Agony II",
            "Agony III",
            "Redlotus",
            "Nirvana",
        )[rank - 1]

    @property
    def start_trophies(self):
        return self.end_trophies - self.trophies_gained


# MEMORIAL ARENA


class MemorialBattle(GenshinModel):
    """Represents weekly performance against a single Memorial Arena boss."""

    score: int
    lineup: List[Battlesuit]
    elf: ELF
    boss: Boss


class MemorialArena(GenshinModel):
    """Represents aggregate weekly performance for the entire Memorial Arena rotation."""

    score: int
    ranking: float = Field(galias="ranking_percentage")
    bracket: str = Field(galias="rank")
    tier: str = Field(galias="area")
    end_time: datetime = Field(galias="time_second")
    battle_data: List[MemorialBattle] = Field(galias="battle_infos")

    @validator("bracket", pre=True)
    def __fix_bracket(cls, rank: int) -> str:
        brackets = (0, 0.20, 2, 7, 17, 35, 65)
        return f"{brackets[rank - 1]:1.2f} ~ {brackets[rank]:1.2f}"

    @validator("tier", pre=True)
    def __fix_difficulty(cls, area: int) -> str:
        return ["Basic", "Elites", "Masters", "Exalted"][area - 1]


# ELYSIAN REALMS


class ElysianRealm(GenshinModel):
    """Represents one completed run of Elysean Realms."""

    completed_at: datetime = Field(galias="settle_time_second")
    score: int
    difficulty: int = Field(galias="punish_level")
    # buffs
    lineup: List[Battlesuit]
    elf: ELF
    remembrance_sigil: Optional[RemembranceSigil] = Field(galias="extra_item_icon")

    @root_validator(pre=True)
    def __pack_lineup(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["lineup"] = [values["main_avatar"], *values["support_avatars"]]
        return values

    @validator("remembrance_sigil", pre=True)
    def __parse_remembrance_sigil(cls, sigil_icon: str):
        match = re.search(r"/(\d+).png", sigil_icon)
        return None if match is None else REMEMBRANCE_SIGILS[int(match[1])]
