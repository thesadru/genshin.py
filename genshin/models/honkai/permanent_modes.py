import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from genshin import models
from genshin.models.honkai import base
from pydantic import Field, root_validator, validator

__all__ = [
    "Boss",
    "ELF",
    "SuperstringAbyss",
    "MemorialBattle",
    "MemorialArena",
    "ElysianRealm",
]


# GENERIC


class Boss(models.APIModel, models.Unique):
    id: int
    name: str
    icon: str = Field(galias="avatar")


class ELF(models.APIModel, models.Unique):

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


def _prettify_abyss_rank(rank: int) -> str:
    """Turn the rank returned by the API into the respective rank name displayed in-game."""
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


class SuperstringAbyss(models.APIModel):
    """Represents one cycle of abyss (3 days per cycle, 2 cycles per week)"""

    score: int
    end_time: datetime = Field(galias="updated_time_second")
    boss: Boss
    lineup: List[base.Battlesuit]
    elf: ELF

    placement: int = Field(galias="rank")
    trophies_gained: int = Field(galias="settled_cup_number")
    end_trophies: int = Field(galias="cup_number")
    start_rank: int = Field(galias="level")
    end_rank: int = Field(galias="settled_level")

    @property
    def start_rank_pretty(self) -> str:
        """Get the rank the user started the abyss cycle with, as displayed in-game."""
        return _prettify_abyss_rank(self.start_rank)

    @property
    def end_rank_pretty(self) -> str:
        """Get the rank the user ended the abyss cycle with, as displayed in-game."""
        return _prettify_abyss_rank(self.end_rank)

    @property
    def start_trophies(self) -> int:
        return self.end_trophies - self.trophies_gained


# MEMORIAL ARENA

# TODO: Remove the need for these


def _prettify_competitive_tier(tier: int) -> str:
    """Turn the tier returned by the API into the respective tier name displayed in-game"""
    return ["Basic", "Elites", "Masters", "Exalted"][tier - 1]


def _prettify_MA_rank(rank: int) -> str:
    """Turn the rank returned by the API into the respective rank name displayed in-game."""
    brackets = (0, 0.20, 2, 7, 17, 35, 65)
    return f"{brackets[rank - 1]:1.2f} ~ {brackets[rank]:1.2f}"


class MemorialBattle(models.APIModel):
    """Represents weekly performance against a single Memorial Arena boss."""

    score: int
    lineup: List[base.Battlesuit]
    elf: ELF
    boss: Boss


class MemorialArena(models.APIModel):
    """Represents aggregate weekly performance for the entire Memorial Arena rotation."""

    score: int
    ranking: float = Field(galias="ranking_percentage")
    rank: int
    tier: int = Field(galias="area")
    end_time: datetime = Field(galias="time_second")
    battle_data: List[MemorialBattle] = Field(galias="battle_infos")

    @property
    def rank_pretty(self) -> str:
        """Returns the user's Memorial Arena rank as displayed in-game."""
        return _prettify_MA_rank(self.rank)

    @property
    def tier_pretty(self) -> str:
        """The user's Memorial Arena tier as displayed in-game."""
        return _prettify_competitive_tier(self.tier)


# ELYSIAN REALMS


class Signet(models.APIModel):
    id: int
    name: str
    icon: str
    number: int

    @root_validator(pre=True)
    def __populate_name(cls, values: Dict[str, Any]):
        values["name"] = [
            "Deliverance",
            "Gold",
            "Decimation",
            "Bodhi",
            "Setsuna",
            "Infinity",
            "Vicissitude",
            "■■",
        ][values["id"] - 1]
        return values

    def get_scaled_icon(self, scale: Literal[1, 2, 3] = 2):
        if not 1 <= scale <= 3:
            raise ValueError("Scale must lie between 1 and 3.")
        return self.icon.replace("@2x", "" if scale == 1 else f"@{scale}x")


class ElysianRealm(models.APIModel):
    """Represents one completed run of Elysean Realms."""

    completed_at: datetime = Field(galias="settle_time_second")
    score: int
    difficulty: int = Field(galias="punish_level")
    signets: List[Signet] = Field(galias="buffs")
    lineup: List[base.Battlesuit]
    elf: ELF
    # TODO: More information with rememberence sigil
    remembrance_sigil: str = Field(galias="extra_item_icon")

    @root_validator(pre=True)
    def __pack_lineup(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Questionable, do we really want to separate them
        # should use a property instead
        values["lineup"] = [values["main_avatar"], *values["support_avatars"]]
        return values
