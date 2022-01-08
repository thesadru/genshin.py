from datetime import datetime
from typing import Any, ClassVar, Dict, List, Union

from pydantic import validator

from genshin import models
from genshin.models.honkai import battlesuit, permanent_modes, record
from pydantic import Field, root_validator

__all__ = [
    "HonkaiStats",
    "HonkaiPartialUserStats",
    "HonkaiUserStats",
    "HonkaiFullUserStats",
]


def _model_to_dict(model: models.APIModel, lang: str = "en-us") -> Dict[str, Any]:
    """Helper function which turns fields into properly named ones"""
    ret = {}
    for field in model.__fields__.values():
        mi18n = model._get_mi18n(field, lang)
        val = getattr(model, field.name)
        if isinstance(val, models.APIModel):
            ret[mi18n] = _model_to_dict(val, lang)
        else:
            ret[mi18n] = val

    return ret


class MemorialArenaStats(models.APIModel):
    """Represents a user's stats regarding the Memorial Arena gamemodes."""

    # fmt: off
    ranking: float = Field(galias="battle_field_ranking_percentage", mi18n="bbs/battle_field_ranking_percentage")
    raw_rank: int =  Field(galias="battle_field_rank",               mi18n="bbs/rank")
    score: int =     Field(galias="battle_field_score",              mi18n="bbs/score")
    raw_tier: int =  Field(galias="battle_field_area",               mi18n="bbs/settled_level")
    # fmt: on

    def as_dict(self, lang: str = "en-us") -> Dict[str, Any]:
        return _model_to_dict(self, lang)

    @property
    def rank(self) -> str:
        """The user's Memorial Arena rank as displayed in-game."""
        return permanent_modes._prettify_MA_rank(self.raw_rank)

    @property
    def tier(self) -> str:
        """The user's Memorial Arena tier as displayed in-game."""
        return permanent_modes._prettify_competitive_tier(self.raw_tier)


class SuperstringAbyssStats(models.APIModel):
    """Represents a user's stats regarding Superstring Abyss."""

    # fmt: off
    raw_rank: int = Field(galias="level",             mi18n="bbs/rank")
    trophies: int = Field(galias="cup_number",        mi18n="bbs/cup_number")
    score: int =    Field(galias="abyss_score",       mi18n="bbs/explain_text_2")
    raw_tier: int = Field(galias="battle_field_area", mi18n="bbs/settled_level")
    # fmt: on
    # for consistency between types; also allows us to forego the mi18n fuckery
    latest_type: ClassVar[str] = "Superstring"

    def as_dict(self, lang: str = "en-us") -> Dict[str, Any]:
        return _model_to_dict(self, lang)

    @property
    def rank(self) -> str:
        """The user's Abyss rank as displayed in-game."""
        # fsr the stats api always returns rank as if the player were lv <81; any tier < 4 works
        return permanent_modes._prettify_abyss_rank(self.raw_rank, 1)

    @property
    def tier(self) -> str:
        """The user's Abyss tier as displayed in-game."""
        return permanent_modes._prettify_competitive_tier(self.raw_tier)


class OldAbyssStats(models.APIModel):
    """Represents a user's stats regarding Q-Singularis and Dirac Sea."""

    # fmt: off
    raw_q_singularis_rank: int = Field(galias="level_of_quantum", mi18n="bbs/Quantum")
    raw_dirac_sea_rank: int =    Field(galias="level_of_ow",      mi18n="bbs/level_of_ow")
    score: int =                 Field(galias="abyss_score",      mi18n="bbs/explain_text_2")
    raw_tier: int =              Field(galias="latest_area",      mi18n="bbs/settled_level")
    raw_latest_rank: int =       Field(galias="latest_level",     mi18n="bbs/rank")
    latest_type: str
    # fmt: on

    @validator("raw_q_singularis_rank", "raw_dirac_sea_rank", "raw_latest_rank", pre=True)
    def __normalize_rank(cls, rank: str) -> int:  # permanent_modes.OldAbyss.__normalize_rank
        return 69 - ord(rank)

    @validator("latest_type")
    def __parse_type(cls, type_: str) -> str:  # permanent_modes.OldAbyss.__parse_type
        return {"OW": "Dirac Sea", "Quantum": "Q-Singularis"}[type_]

    @property
    def q_singularis_rank(self) -> str:
        """The user's latest Q-singularis rank as displayed in-game."""
        return permanent_modes._prettify_abyss_rank(self.raw_q_singularis_rank, self.raw_tier)

    @property
    def dirac_sea_rank(self) -> str:
        """The user's latest Dirac Sea rank as displayed in-game."""
        return permanent_modes._prettify_abyss_rank(self.raw_dirac_sea_rank, self.raw_tier)

    @property
    def latest_rank(self) -> str:
        """The user's latest abyss rank as displayed in-game. Seems to apply after weekly reset,
        so this may differ from the user's Dirac Sea/Q-Singularis ranks if their rank changed.
        """
        return permanent_modes._prettify_abyss_rank(self.raw_latest_rank, self.raw_tier)

    @property
    def tier(self) -> str:
        """The user's Abyss tier as displayed in-game."""
        return permanent_modes._prettify_competitive_tier(self.raw_tier)

    def as_dict(self, lang: str = "en-us") -> Dict[str, Any]:
        return _model_to_dict(self, lang)


class ElysianRealmStats(models.APIModel):
    """Represents a user's stats regarding Elysian Realms."""

    # fmt: off
    highest_difficulty: int = Field(galias="god_war_max_punish_level",        mi18n="bbs/god_war_max_punish_level")
    remembrance_sigils: int = Field(galias="god_war_extra_item_number",       mi18n="bbs/god_war_extra_item_number")
    highest_score: int =      Field(galias="god_war_max_challenge_score",     mi18n="bbs/god_war_max_challenge_score")
    highest_floor: int =      Field(galias="god_war_max_challenge_level",     mi18n="bbs/rogue_setted_level")
    max_level_suits: int =    Field(galias="god_war_max_level_avatar_number", mi18n="bbs/explain_text_6")
    # fmt: on

    def as_dict(self, lang: str = "en-us") -> Dict[str, Any]:
        return _model_to_dict(self, lang)


class HonkaiStats(models.APIModel):
    """Represents a user's stat page"""

    # fmt: off
    active_days: int =     Field(galias="active_day_number",         mi18n="bbs/active_day_number")
    achievements: int =    Field(galias="achievement_number",        mi18n="bbs/achievment_complete_count")

    battlesuits: int =     Field(galias="armor_number",              mi18n="bbs/armor_number")
    battlesuits_SSS: int = Field(galias="sss_armor_number",          mi18n="bbs/sss_armor_number")
    stigmata: int =        Field(galias="stigmata_number",           mi18n="bbs/stigmata_number")
    stigmata_5star: int =  Field(galias="five_star_stigmata_number", mi18n="bbs/stigmata_number_5")
    weapons: int =         Field(galias="weapon_number",             mi18n="bbs/weapon_number")
    weapons_5star: int =   Field(galias="five_star_weapon_number",   mi18n="bbs/weapon_number_5")
    outfits: int =         Field(galias="suit_number",               mi18n="bbs/suit_number")

    abyss: Union[SuperstringAbyssStats, OldAbyssStats] = Field(mi18n="bbs/explain_text_1")
    memorial_arena: MemorialArenaStats =                 Field(mi18n="bbs/battle_field_ranking_percentage")
    elysian_realm: ElysianRealmStats =                   Field(mi18n="bbs/godwor")
    # fmt: on

    @root_validator(pre=True)
    def __pack_gamemode_stats(cls, values: Dict[str, Any]):
        abyss_data = values.get("new_abyss")
        if abyss_data:  # Superstring
            values["abyss"] = SuperstringAbyssStats(**abyss_data, **values)
        else:  # Either of the other two
            abyss_data = values["old_abyss"]
            values["abyss"] = OldAbyssStats(**abyss_data, **values)
        values["memorial_arena"] = MemorialArenaStats(**values)
        values["elysian_realm"] = ElysianRealmStats(**values)
        return values

    def as_dict(self, lang: str = "en-us") -> Dict[str, Any]:
        return _model_to_dict(self, lang)


class HonkaiPartialUserStats(models.APIModel):
    """Represents basic user stats, showing only generic user data and stats."""

    info: record.UserInfo = Field(galias="role")
    stats: HonkaiStats

    # Absolutely no clue what this is for
    preference: Dict[str, str]


class HonkaiUserStats(HonkaiPartialUserStats):
    """Represents a user's stats, including characters and their gear"""

    battlesuits: List[battlesuit.FullBattlesuit]


class HonkaiFullUserStats(HonkaiUserStats):
    """Represents a user's full stats, including characters, gear, and gamemode data"""

    abyss: List[Union[permanent_modes.SuperstringAbyss, permanent_modes.OldAbyss]]
    memorial_arena: List[permanent_modes.MemorialArena]
    elysian_realm: permanent_modes.ElysianRealms

    @property
    def abyss_superstring(self) -> List[permanent_modes.SuperstringAbyss]:
        """Filter `self.abyss` to only return instances of Superstring Abyss."""
        return [
            entry for entry in self.abyss if isinstance(entry, permanent_modes.SuperstringAbyss)
        ]

    @property
    def abyss_q_singularis(self) -> List[permanent_modes.OldAbyss]:
        """Filter `self.abyss` to only return instances of Q-Singularis."""
        return [
            entry
            for entry in self.abyss
            if isinstance(entry, permanent_modes.OldAbyss) and entry.type == "Q-Singularis"
        ]

    @property
    def abyss_dirac_sea(self) -> List[permanent_modes.OldAbyss]:
        """Filter `self.abyss` to only return instances of Dirac Sea."""
        return [
            entry
            for entry in self.abyss
            if isinstance(entry, permanent_modes.OldAbyss) and entry.type == "Dirac Sea"
        ]
