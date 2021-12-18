import abc
from typing import Any, Dict, List

from pydantic import Field, root_validator, validator

from .base import GenshinModel
from .honkai_character import FullBattlesuit
from .honkai_hoyolab import UserInfo
from .honkai_permanent_modes import SuperstringAbyss, MemorialArena, ElysianRealm
from .honkai_permanent_modes import (
    _prettify_abyss_rank,
    _prettify_MA_rank,
    _prettify_competitive_tier,
)

__all__ = (
    "BaseStats",
    "HonkaiStats",
    "HonkaiPartialUserStats",
    "HonkaiUserStats",
    "HonkaiFullUserStats",
)


# Could be used as a base class for HonkaiStats and GenshinStats
class BaseStats(GenshinModel, abc.ABC):
    def as_dict(self, lang: str = "en-us") -> Dict[str, Any]:
        """Helper function which turns fields into properly named ones"""
        return {
            self._get_mi18n(field, lang): getattr(self, field.name)
            for field in self.__fields__.values()
        }


class HonkaiStats(BaseStats):
    """Represents a user's stat page"""

    # TODO: Figure out mi18n locations
    # fmt: off
    active_days: int =           Field(galias="active_day_number",               mi18n="")
    achievements: int =          Field(galias="achievement_number",              mi18n="")

    battlesuits: int =           Field(galias="armor_number",                    mi18n="")
    battlesuits_SSS: int =       Field(galias="sss_armor_number",                mi18n="")
    stigmata: int =              Field(galias="stigmata_number",                 mi18n="")
    stigmata_5star: int =        Field(galias="five_star_stigmata_number",       mi18n="")
    weapons: int =               Field(galias="weapon_number",                   mi18n="")
    weapons_5star: int =         Field(galias="five_star_weapon_number",         mi18n="")
    outfits: int =               Field(galias="suit_number",                     mi18n="")

    # Perhaps combine these by category (MA, Abyss, ER) into submodels?
    MA_ranking: float =          Field(galias="battle_field_ranking_percentage", mi18n="")
    MA_rank: int =               Field(galias="battle_field_rank",               mi18n="")
    MA_score: int =              Field(galias="battle_field_score",              mi18n="")
    MA_tier: int =               Field(galias="battle_field_area",               mi18n="")
    abyss_rank: int =            Field(                                          mi18n="")
    abyss_trophies: int =        Field(                                          mi18n="")
    abyss_trophies_won: int =    Field(galias="abyss_score",                     mi18n="")
    ER_highest_difficulty: int = Field(galias="god_war_max_punish_level",        mi18n="")
    ER_remembrance_sigils: int = Field(galias="god_war_extra_item_number",       mi18n="")
    ER_highest_score: int =      Field(galias="god_war_max_challenge_score",     mi18n="")
    ER_highest_floor: int =      Field(galias="god_war_max_challenge_level",     mi18n="")
    ER_max_level_suits: int =    Field(galias="god_war_max_level_avatar_number", mi18n="")
    # fmt: on

    @root_validator(pre=True)
    def __unpack_abyss(cls, values: Dict[str, Any]):
        # NOTE: Alternative: combine both 'subfields' into one string, e.g.:
        # "RedLotus (1550 trophies)"
        # this would probably play a bit more nicely with the mi18n names

        abyss = values["new_abyss"]
        values["abyss_rank"] = abyss["level"]
        values["abyss_trophies"] = abyss["cup_number"]
        return values

    @property
    def MA_rank_pretty(self) -> str:
        """Returns the user's Memorial Arena rank as displayed in-game."""
        return _prettify_MA_rank(self.MA_rank)

    @property
    def MA_tier_pretty(self) -> str:
        """Returns the user's Memorial Arena tier as displayed in-game."""
        return _prettify_competitive_tier(self.MA_rank)

    @property
    def abyss_rank_pretty(self) -> str:
        """Returns the user's Abyss rank as displayed in-game."""
        return _prettify_abyss_rank(self.abyss_rank)


class HonkaiPartialUserStats(GenshinModel):
    """Represents basic user stats, showing only generic user data and stats."""

    info: UserInfo = Field(galias="role")
    stats: HonkaiStats

    # Absolutely no clue what this is for
    preference: Dict[str, str]


class HonkaiUserStats(HonkaiPartialUserStats):
    """Represents a user's stats, including characters and their gear"""

    battlesuits: List[FullBattlesuit]


class HonkaiFullUserStats(HonkaiUserStats):
    """Represents a user's full stats, including characters, gear, and gamemode data"""

    # TODO: change abyss to List[Union[AbyssMode1 | AbyssMode2 | ...]]
    #       gonna be annoying as that'd make the typehinting a lot less useful.

    abyss: List[SuperstringAbyss]
    memorial_arena: List[MemorialArena]
    elysian_realm: List[ElysianRealm]
