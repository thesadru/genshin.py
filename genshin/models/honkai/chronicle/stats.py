"""Honkai stats models."""
import typing

import pydantic

from genshin.models.model import Aliased, APIModel

from . import battlesuits, modes

__all__ = [
    "FullHonkaiUserStats",
    "HonkaiStats",
    "HonkaiUserStats",
]


def _model_to_dict(model: APIModel, lang: str = "en-us") -> typing.Mapping[str, typing.Any]:
    """Helper function which turns fields into properly named ones"""
    ret: typing.Dict[str, typing.Any] = {}
    for field in model.__fields__.values():
        mi18n = model._get_mi18n(field, lang)
        val = getattr(model, field.name)
        if isinstance(val, APIModel):
            ret[mi18n] = _model_to_dict(val, lang)
        else:
            ret[mi18n] = val

    return ret


# flake8: noqa: E222
class MemorialArenaStats(APIModel):
    """Represents a user's stats regarding the Memorial Arena gamemodes."""

    _stat_lang: str = "en-us"

    # fmt: off
    ranking: float = Aliased("battle_field_ranking_percentage", mi18n="bbs/battle_field_ranking_percentage")
    raw_rank: int =  Aliased("battle_field_rank",               mi18n="bbs/rank")
    score: int =     Aliased("battle_field_score",              mi18n="bbs/score")
    raw_tier: int =  Aliased("battle_field_area",               mi18n="bbs/settled_level")
    # fmt: on

    @pydantic.validator("ranking", pre=True)
    def __normalize_ranking(cls, value: typing.Union[str, float]) -> float:
        return float(value) if value else 0

    def as_dict(self, lang: str = "en-us") -> typing.Mapping[str, typing.Any]:
        return _model_to_dict(self, lang)

    @property
    def rank(self) -> str:
        """The user's Memorial Arena rank as displayed in-game."""
        return modes.prettify_MA_rank(self.raw_rank)

    @property
    def tier(self) -> str:
        """The user's Memorial Arena tier as displayed in-game."""
        return self.get_tier()

    def get_tier(self, lang: typing.Optional[str] = None) -> str:
        """Get the user's Memorial Arena tier in a specific language."""
        key = modes.get_competitive_tier_mi18n(self.raw_tier)
        return self._get_mi18n(key, lang or self._stat_lang)


# flake8: noqa: E222
class SuperstringAbyssStats(APIModel):
    """Represents a user's stats regarding Superstring Abyss."""

    _stat_lang: str = "en-us"

    # fmt: off
    raw_rank: int = Aliased("level",             mi18n="bbs/rank")
    trophies: int = Aliased("cup_number",        mi18n="bbs/cup_number")
    score: int =    Aliased("abyss_score",       mi18n="bbs/explain_text_2")
    raw_tier: int = Aliased("battle_field_area", mi18n="bbs/settled_level")
    # fmt: on

    # for consistency between types; also allows us to forego the mi18n fuckery
    latest_type: typing.ClassVar[str] = "Superstring"

    def as_dict(self, lang: str = "en-us") -> typing.Mapping[str, typing.Any]:
        return _model_to_dict(self, lang)

    @property
    def rank(self) -> str:
        """The user's Abyss rank as displayed in-game."""
        return self.get_rank()

    def get_rank(self, lang: typing.Optional[str] = None) -> str:
        """Get the user's Abyss rank in a specific language."""
        key = modes.get_abyss_rank_mi18n(self.raw_rank, self.raw_tier)
        return self._get_mi18n(key, lang or self._stat_lang)

    @property
    def tier(self) -> str:
        """The user's Abyss tier as displayed in-game."""
        return self.get_tier()

    def get_tier(self, lang: typing.Optional[str] = None) -> str:
        """Get the user's Abyss tier in a specific language."""
        key = modes.get_competitive_tier_mi18n(self.raw_tier)
        return self._get_mi18n(key, lang or self._stat_lang)


# flake8: noqa: E222
class OldAbyssStats(APIModel):
    """Represents a user's stats regarding Q-Singularis and Dirac Sea."""

    _stat_lang: str = "en-us"

    # fmt: off
    raw_q_singularis_rank: typing.Optional[int] = Aliased("level_of_quantum", mi18n="bbs/Quantum")
    raw_dirac_sea_rank: typing.Optional[int] =    Aliased("level_of_ow",      mi18n="bbs/level_of_ow")
    score: int =                                  Aliased("abyss_score",      mi18n="bbs/explain_text_2")
    raw_tier: int =                               Aliased("latest_area",      mi18n="bbs/settled_level")
    raw_latest_rank: typing.Optional[int] =       Aliased("latest_level",     mi18n="bbs/rank")
    # TODO: Add proper key
    latest_type: str =                            Aliased(                    mi18n="bbs/latest_type")  
    # fmt: on

    @pydantic.validator("raw_q_singularis_rank", "raw_dirac_sea_rank", "raw_latest_rank", pre=True)
    def __normalize_rank(cls, rank: str) -> typing.Optional[int]:  # modes.OldAbyss.__normalize_rank
        if "Unknown" in rank:
            return None

        return 69 - ord(rank)

    @property
    def q_singularis_rank(self) -> typing.Optional[str]:
        """The user's latest Q-Singularis rank as displayed in-game."""
        if self.raw_q_singularis_rank is None:
            return None

        return self.get_rank(self.raw_q_singularis_rank)

    @property
    def dirac_sea_rank(self) -> typing.Optional[str]:
        """The user's latest Dirac Sea rank as displayed in-game."""
        if self.raw_dirac_sea_rank is None:
            return None

        return self.get_rank(self.raw_dirac_sea_rank)

    @property
    def latest_rank(self) -> typing.Optional[str]:
        """The user's latest Abyss rank as displayed in-game. Seems to apply after weekly reset,
        so this may differ from the user's Dirac Sea/Q-Singularis ranks if their rank changed.
        """
        if self.raw_latest_rank is None:
            return None

        return self.get_rank(self.raw_latest_rank)

    def get_rank(self, rank: int, lang: typing.Optional[str] = None) -> str:
        """Get the user's Abyss rank in a specific language.

        Must be supplied with one of the raw ranks stored on this class.
        """
        key = modes.get_abyss_rank_mi18n(rank, self.raw_tier)
        return self._get_mi18n(key, lang or self._stat_lang)

    @property
    def tier(self) -> str:
        """The user's Abyss tier as displayed in-game."""
        return modes.get_competitive_tier_mi18n(self.raw_tier)

    def get_tier(self, lang: typing.Optional[str] = None) -> str:
        """Get the user's Abyss tier in a specific language."""
        key = modes.get_competitive_tier_mi18n(self.raw_tier)
        return self._get_mi18n(key, lang or self._stat_lang)

    def as_dict(self, lang: str = "en-us") -> typing.Mapping[str, typing.Any]:
        return _model_to_dict(self, lang)


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

    def as_dict(self, lang: str = "en-us") -> typing.Mapping[str, typing.Any]:
        return _model_to_dict(self, lang)


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
    def __pack_gamemode_stats(cls, values: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        if "new_abyss" in values:
            values["abyss"] = SuperstringAbyssStats(**values["new_abyss"], **values)
        elif "old_abyss" in values:
            values["abyss"] = OldAbyssStats(**values["old_abyss"], **values)

        if "memorial_arena" not in values:
            values["memorial_arena"] = MemorialArenaStats(**values)

        if "elysian_realm" not in values:
            values["elysian_realm"] = ElysianRealmStats(**values)

        return values

    def as_dict(self, lang: str = "en-us") -> typing.Mapping[str, typing.Any]:
        return _model_to_dict(self, lang)


class UserInfo(APIModel):
    """Honkai user info."""

    nickname: str
    region: str
    level: int
    icon: str = Aliased("AvatarUrl")


class HonkaiUserStats(APIModel):
    """Represents basic user stats, showing only generic user data and stats."""

    info: UserInfo = Aliased("role")
    stats: HonkaiStats


class FullHonkaiUserStats(HonkaiUserStats):
    """Represents a user's full stats, including characters, gear, and gamemode data"""

    battlesuits: typing.Sequence[battlesuits.FullBattlesuit]
    abyss: typing.Sequence[typing.Union[modes.SuperstringAbyss, modes.OldAbyss]]
    memorial_arena: typing.Sequence[modes.MemorialArena]
    elysian_realm: typing.Sequence[modes.ElysianRealm]

    @property
    def abyss_superstring(self) -> typing.Sequence[modes.SuperstringAbyss]:
        """Filter `self.abyss` to only return instances of Superstring Abyss."""
        return [entry for entry in self.abyss if isinstance(entry, modes.SuperstringAbyss)]

    @property
    def abyss_q_singularis(self) -> typing.Sequence[modes.OldAbyss]:
        """Filter `self.abyss` to only return instances of Q-Singularis."""
        return [entry for entry in self.abyss if isinstance(entry, modes.OldAbyss) and entry.type == "Q-Singularis"]

    @property
    def abyss_dirac_sea(self) -> typing.Sequence[modes.OldAbyss]:
        """Filter `self.abyss` to only return instances of Dirac Sea."""
        return [entry for entry in self.abyss if isinstance(entry, modes.OldAbyss) and entry.type == "Dirac Sea"]
