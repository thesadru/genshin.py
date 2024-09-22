"""Honkai stats models."""

import typing

import pydantic

from genshin.models import hoyolab
from genshin.models.model import Aliased, APIModel

from . import battlesuits as honkai_battlesuits
from . import modes

__all__ = ["FullHonkaiUserStats", "HonkaiStats", "HonkaiUserStats"]


# flake8: noqa: E222
class MemorialArenaStats(APIModel):
    """Represents a user's stats regarding the Memorial Arena gamemodes."""

    ranking: float = Aliased("battle_field_ranking_percentage")
    raw_rank: int = Aliased("battle_field_rank")
    score: int = Aliased("battle_field_score")
    raw_tier: int = Aliased("battle_field_area")

    @pydantic.field_validator("ranking", mode="before")
    def __normalize_ranking(cls, value: typing.Union[str, float]) -> float:
        return float(value) if value else 0

    @property
    def rank(self) -> str:
        """The user's Memorial Arena rank as displayed in-game."""
        return modes.prettify_MA_rank(self.raw_rank)


# flake8: noqa: E222
class SuperstringAbyssStats(APIModel):
    """Represents a user's stats regarding Superstring Abyss."""

    raw_rank: int = Aliased("level")
    trophies: int = Aliased("cup_number")
    score: int = Aliased("abyss_score")
    raw_tier: int = Aliased("battle_field_area")

    # for consistency between types; also allows us to forego the mi18n fuckery
    latest_type: typing.ClassVar[str] = "Superstring"


# flake8: noqa: E222
class OldAbyssStats(APIModel):
    """Represents a user's stats regarding Q-Singularis and Dirac Sea."""

    raw_q_singularis_rank: typing.Optional[int] = Aliased("level_of_quantum")
    raw_dirac_sea_rank: typing.Optional[int] = Aliased("level_of_ow")
    score: int = Aliased("abyss_score")
    raw_tier: int = Aliased("latest_area")
    raw_latest_rank: typing.Optional[int] = Aliased("latest_level")
    # TODO: Add proper key
    latest_type: str = Aliased()

    @pydantic.field_validator("raw_q_singularis_rank", "raw_dirac_sea_rank", "raw_latest_rank", mode="before")
    def __normalize_rank(cls, rank: typing.Optional[str]) -> typing.Optional[int]:  # modes.OldAbyss.__normalize_rank
        if isinstance(rank, int):
            return rank

        if rank is None or "Unknown" in rank:
            return None

        return 69 - ord(rank)

    model_config: pydantic.ConfigDict = pydantic.ConfigDict(frozen=False)  # type: ignore


# flake8: noqa: E222
class ElysianRealmStats(APIModel):
    """Represents a user's stats regarding Elysian Realms."""

    highest_difficulty: int = Aliased("god_war_max_punish_level")
    remembrance_sigils: int = Aliased("god_war_extra_item_number")
    highest_score: int = Aliased("god_war_max_challenge_score")
    highest_floor: int = Aliased("god_war_max_challenge_level")
    max_level_suits: int = Aliased("god_war_max_level_avatar_number")


class HonkaiStats(APIModel):
    """Represents a user's stat page"""

    active_days: int = Aliased("active_day_number")
    achievements: int = Aliased("achievement_number")

    battlesuits: int = Aliased("armor_number")
    battlesuits_SSS: int = Aliased("sss_armor_number")
    stigmata: int = Aliased("stigmata_number")
    stigmata_5star: int = Aliased("five_star_stigmata_number")
    weapons: int = Aliased("weapon_number")
    weapons_5star: int = Aliased("five_star_weapon_number")
    outfits: int = Aliased("suit_number")

    abyss: typing.Union[SuperstringAbyssStats, OldAbyssStats] = Aliased()
    memorial_arena: MemorialArenaStats = Aliased()
    elysian_realm: ElysianRealmStats = Aliased()

    @pydantic.model_validator(mode="before")
    def __pack_gamemode_stats(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if "new_abyss" in values:
            values["abyss"] = SuperstringAbyssStats(**values["new_abyss"], **values)
        elif "old_abyss" in values:
            values["abyss"] = OldAbyssStats(**values["old_abyss"], **values)

        if "memorial_arena" not in values:
            values["memorial_arena"] = MemorialArenaStats(**values)

        if "elysian_realm" not in values:
            values["elysian_realm"] = ElysianRealmStats(**values)

        return values


class HonkaiUserStats(APIModel):
    """Represents basic user stats, showing only generic user data and stats."""

    info: hoyolab.UserInfo = Aliased("role")
    stats: HonkaiStats


class FullHonkaiUserStats(HonkaiUserStats):
    """Represents a user's full stats, including characters, gear, and gamemode data"""

    battlesuits: typing.Sequence[honkai_battlesuits.FullBattlesuit]
    abyss: typing.Sequence[typing.Union[modes.SuperstringAbyss, modes.OldAbyss]]
    memorial_arena: typing.Sequence[modes.MemorialArena]
    elysian_realm: typing.Sequence[modes.ElysianRealm]

    @property
    def abyss_superstring(self) -> typing.Sequence[modes.SuperstringAbyss]:
        """Filter `self.abyss` to only return instances of Superstring Abyss."""
        return [entry for entry in self.abyss if isinstance(entry, modes.SuperstringAbyss)]
