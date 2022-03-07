import typing

import pydantic

from genshin.models.model import Aliased, APIModel

__all__ = [
    "HonkaiStats",
    "HonkaiPartialUserStats",
]


# flake8: noqa: E222
class MemorialArenaStats(APIModel):
    """Represents a user's stats regarding the Memorial Arena gamemodes."""

    # fmt: off
    ranking: float = Aliased("battle_field_ranking_percentage", mi18n="bbs/battle_field_ranking_percentage")
    raw_rank: int =  Aliased("battle_field_rank",               mi18n="bbs/rank")
    score: int =     Aliased("battle_field_score",              mi18n="bbs/score")
    raw_tier: int =  Aliased("battle_field_area",               mi18n="bbs/settled_level")
    # fmt: on

    # @property
    # def rank(self) -> str:
    #     """The user's Memorial Arena rank as displayed in-game."""
    #     return permanent_modes._prettify_MA_rank(self.raw_rank)

    # @property
    # def tier(self) -> str:
    #     """The user's Memorial Arena tier as displayed in-game."""
    #     return permanent_modes._prettify_competitive_tier(self.raw_tier)


# flake8: noqa: E222
class SuperstringAbyssStats(APIModel):
    """Represents a user's stats regarding Superstring Abyss."""

    # fmt: off
    raw_rank: int = Aliased("level",             mi18n="bbs/rank")
    trophies: int = Aliased("cup_number",        mi18n="bbs/cup_number")
    score: int =    Aliased("abyss_score",       mi18n="bbs/explain_text_2")
    raw_tier: int = Aliased("battle_field_area", mi18n="bbs/settled_level")
    # fmt: on

    # for consistency between types; also allows us to forego the mi18n fuckery
    latest_type: typing.ClassVar[str] = "Superstring"

    # @property
    # def rank(self) -> str:
    #     """The user's Abyss rank as displayed in-game."""
    #     # fsr the stats api always returns rank as if the player were lv <81; any tier < 4 works
    #     return permanent_modes._prettify_abyss_rank(self.raw_rank, 1)

    # @property
    # def tier(self) -> str:
    #     """The user's Abyss tier as displayed in-game."""
    #     return permanent_modes._prettify_competitive_tier(self.raw_tier)


# flake8: noqa: E222
class OldAbyssStats(APIModel):
    """Represents a user's stats regarding Q-Singularis and Dirac Sea."""

    # fmt: off
    raw_q_singularis_rank: int = Aliased("level_of_quantum", mi18n="bbs/Quantum")
    raw_dirac_sea_rank: int =    Aliased("level_of_ow",      mi18n="bbs/level_of_ow")
    score: int =                 Aliased("abyss_score",      mi18n="bbs/explain_text_2")
    raw_tier: int =              Aliased("latest_area",      mi18n="bbs/settled_level")
    raw_latest_rank: int =       Aliased("latest_level",     mi18n="bbs/rank")
    latest_type: str
    # fmt: on

    @pydantic.validator("raw_q_singularis_rank", "raw_dirac_sea_rank", "raw_latest_rank", pre=True)
    def __normalize_rank(cls, rank: str) -> int:  # permanent_modes.OldAbyss.__normalize_rank
        return 69 - ord(rank)

    @pydantic.validator("latest_type")
    def __parse_type(cls, type_: str) -> str:  # permanent_modes.OldAbyss.__parse_type
        return {"OW": "Dirac Sea", "Quantum": "Q-Singularis"}[type_]

    # @property
    # def q_singularis_rank(self) -> str:
    #     """The user's latest Q-singularis rank as displayed in-game."""
    #     return permanent_modes._prettify_abyss_rank(self.raw_q_singularis_rank, self.raw_tier)

    # @property
    # def dirac_sea_rank(self) -> str:
    #     """The user's latest Dirac Sea rank as displayed in-game."""
    #     return permanent_modes._prettify_abyss_rank(self.raw_dirac_sea_rank, self.raw_tier)

    # @property
    # def latest_rank(self) -> str:
    #     """The user's latest abyss rank as displayed in-game. Seems to apply after weekly reset,
    #     so this may differ from the user's Dirac Sea/Q-Singularis ranks if their rank changed.
    #     """
    #     return permanent_modes._prettify_abyss_rank(self.raw_latest_rank, self.raw_tier)

    # @property
    # def tier(self) -> str:
    #     """The user's Abyss tier as displayed in-game."""
    #     return permanent_modes._prettify_competitive_tier(self.raw_tier)


# flake8: noqa: E222
class ElysianRealmStats(APIModel):
    """Represents a user's stats regarding Elysian Realms."""

    # fmt: off
    highest_difficulty: int = Aliased("god_war_max_punish_level",        mi18n="bbs/god_war_max_punish_level")
    remembrance_sigils: int = Aliased("god_war_extra_item_number",       mi18n="bbs/god_war_extra_item_number")
    highest_score: int =      Aliased("god_war_max_challenge_score",     mi18n="bbs/god_war_max_challenge_score")
    highest_floor: int =      Aliased("god_war_max_challenge_level",     mi18n="bbs/rogue_setted_level")
    max_level_suits: int =    Aliased("god_war_max_level_avatar_number", mi18n="bbs/explain_text_6")
    # fmt: on


class HonkaiStats(APIModel):
    """Represents a user's stat page"""

    # fmt: off
    active_days: int =     Aliased("active_day_number",         mi18n="bbs/active_day_number")
    achievements: int =    Aliased("achievement_number",        mi18n="bbs/achievment_complete_count")

    battlesuits: int =     Aliased("armor_number",              mi18n="bbs/armor_number")
    battlesuits_SSS: int = Aliased("sss_armor_number",          mi18n="bbs/sss_armor_number")
    stigmata: int =        Aliased("stigmata_number",           mi18n="bbs/stigmata_number")
    stigmata_5star: int =  Aliased("five_star_stigmata_number", mi18n="bbs/stigmata_number_5")
    weapons: int =         Aliased("weapon_number",             mi18n="bbs/weapon_number")
    weapons_5star: int =   Aliased("five_star_weapon_number",   mi18n="bbs/weapon_number_5")
    outfits: int =         Aliased("suit_number",               mi18n="bbs/suit_number")
    # fmt: on

    abyss: typing.Union[SuperstringAbyssStats, OldAbyssStats] = Aliased(mi18n="bbs/explain_text_1")
    memorial_arena: MemorialArenaStats = Aliased(mi18n="bbs/battle_field_ranking_percentage")
    elysian_realm: ElysianRealmStats = Aliased(mi18n="bbs/godwor")

    @pydantic.root_validator(pre=True)
    def __pack_gamemode_stats(cls, values: typing.Dict[str, typing.Any]):
        abyss_data = values.get("new_abyss")

        if abyss_data:
            # Superstring
            values["abyss"] = SuperstringAbyssStats(**abyss_data, **values)
        else:
            # Either of the other two
            abyss_data = values["old_abyss"]
            values["abyss"] = OldAbyssStats(**abyss_data, **values)

        values["memorial_arena"] = MemorialArenaStats(**values)
        values["elysian_realm"] = ElysianRealmStats(**values)

        return values


class UserInfo(APIModel):
    """Honkai user info."""

    nickname: str
    region: str
    level: int
    icon: str = Aliased("AvatarUrl")


class HonkaiPartialUserStats(APIModel):
    """Represents basic user stats, showing only generic user data and stats."""

    info: UserInfo = Aliased("role")
    stats: HonkaiStats
