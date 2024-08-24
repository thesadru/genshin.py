"""Honkai stats models."""

import typing

import pydantic

from genshin.models import hoyolab
from genshin.models.model import APIModel

from . import battlesuits as honkai_battlesuits
from . import modes

__all__ = [
    "FullHonkaiUserStats",
    "HonkaiStats",
    "HonkaiUserStats",
]


# flake8: noqa: E222
class MemorialArenaStats(APIModel):
    """Represents a user's stats regarding the Memorial Arena gamemodes."""

    ranking: float = pydantic.Field(alias="battle_field_ranking_percentage")
    rank: int = pydantic.Field(alias="battle_field_rank")
    score: int = pydantic.Field(alias="battle_field_score")
    tier: int = pydantic.Field(alias="battle_field_area")

    @pydantic.field_validator("ranking", mode="before")
    @classmethod
    def __normalize_ranking(cls, value: typing.Union[str, float]) -> float:
        return float(value) if value else 0


# flake8: noqa: E222
class SuperstringAbyssStats(APIModel):
    """Represents a user's stats regarding Superstring Abyss."""

    rank: int = pydantic.Field(alias="level")
    trophies: int = pydantic.Field(alias="cup_number")
    score: int = pydantic.Field(alias="abyss_score")
    tier: int = pydantic.Field(alias="battle_field_area")

    # for consistency between types; also allows us to forego the mi18n fuckery
    latest_type: typing.ClassVar[str] = "Superstring"


# flake8: noqa: E222
class OldAbyssStats(APIModel):
    """Represents a user's stats regarding Q-Singularis and Dirac Sea."""

    q_singularis_rank: typing.Optional[int] = pydantic.Field(alias="level_of_quantum")
    dirac_sea_rank: typing.Optional[int] = pydantic.Field(alias="level_of_ow")
    score: int = pydantic.Field(alias="abyss_score")
    tier: int = pydantic.Field(alias="latest_area")
    latest_rank: typing.Optional[int] = pydantic.Field(alias="latest_level")
    latest_type: str

    @pydantic.field_validator("q_singularis_rank", "dirac_sea_rank", "latest_rank", mode="before")
    @classmethod
    def __normalize_rank(cls, rank: typing.Optional[str]) -> typing.Optional[int]:  # modes.OldAbyss.__normalize_rank
        if isinstance(rank, int):
            return rank

        if rank is None or "Unknown" in rank:
            return None

        return ord("E") - ord(rank)

    class Config:
        # this is for the "stat_lang" field, hopefully nobody abuses this
        allow_mutation = True


# flake8: noqa: E222
class ElysianRealmStats(APIModel):
    """Represents a user's stats regarding Elysian Realms."""

    highest_difficulty: int = pydantic.Field(alias="god_war_max_punish_level")
    remembrance_sigils: int = pydantic.Field(alias="god_war_extra_item_number")
    highest_score: int = pydantic.Field(alias="god_war_max_challenge_score")
    highest_floor: int = pydantic.Field(alias="god_war_max_challenge_level")
    max_level_suits: int = pydantic.Field(alias="god_war_max_level_avatar_number")


class HonkaiStats(APIModel):
    """Represents a user's stat page"""

    active_days: int = pydantic.Field(alias="active_day_number")
    achievements: int = pydantic.Field(alias="achievement_number")

    battlesuits: int = pydantic.Field(alias="armor_number")
    battlesuits_SSS: int = pydantic.Field(alias="sss_armor_number")
    stigmata: int = pydantic.Field(alias="stigmata_number")
    stigmata_5star: int = pydantic.Field(alias="five_star_stigmata_number")
    weapons: int = pydantic.Field(alias="weapon_number")
    weapons_5star: int = pydantic.Field(alias="five_star_weapon_number")
    outfits: int = pydantic.Field(alias="suit_number")

    abyss: typing.Union[SuperstringAbyssStats, OldAbyssStats]
    memorial_arena: MemorialArenaStats
    elysian_realm: ElysianRealmStats

    @pydantic.model_validator(mode="before")
    @classmethod
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


class HonkaiUserStats(APIModel):
    """Represents basic user stats, showing only generic user data and stats."""

    info: hoyolab.UserInfo = pydantic.Field(alias="role")
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

    @property
    def abyss_q_singularis(self) -> typing.Sequence[modes.OldAbyss]:
        """Filter `self.abyss` to only return instances of Q-Singularis."""
        return [entry for entry in self.abyss if isinstance(entry, modes.OldAbyss) and entry.type == "Q-Singularis"]

    @property
    def abyss_dirac_sea(self) -> typing.Sequence[modes.OldAbyss]:
        """Filter `self.abyss` to only return instances of Dirac Sea."""
        return [entry for entry in self.abyss if isinstance(entry, modes.OldAbyss) and entry.type == "Dirac Sea"]
