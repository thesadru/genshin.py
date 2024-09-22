"""Honkai battle chronicle models."""

from __future__ import annotations

import datetime
import re
import typing

import pydantic

from genshin.models.honkai import battlesuit
from genshin.models.model import Aliased, APIModel, Unique

__all__ = ["ELF", "Boss", "ElysianRealm", "MemorialArena", "MemorialBattle", "OldAbyss", "SuperstringAbyss"]

REMEMBRANCE_SIGILS: dict[int, tuple[str, int]] = {
    119301: ("The MOTH Insignia", 1),
    119302: ("Home Lost", 1),
    119303: ("False Hope", 1),
    119304: ("Tin Flask", 1),
    119305: ("Ruined Legacy", 1),
    119306: ("Burden", 2),
    119307: ("Gold Goblet", 2),
    119308: ("Mad King's Mask", 2),
    119309: ("Light as a Bodhi Leaf", 2),
    119310: ("Forget-Me-Not", 2),
    119311: ("Forbidden Seed", 2),
    119312: ("Memory", 2),
    119313: ("Crystal Rose", 2),
    119314: ("Abandoned", 3),
    119315: ("Good Old Days", 3),
    119316: ("Shattered Shackles", 3),
    119317: ("Heavy as a Million Lives", 3),
    119318: ("Stained Sakura", 3),
    119319: ("The First Scale", 3),
    119320: ("Resolve", 3),
    119321: ("Thorny Crown", 3),
    119326: ("Veil of Tears", 2),
    119327: ("Pseudo Miracle", 2),
    119328: ("Fragile Friend", 2),
    119329: ("Rainbow of Absence", 2),
    119330: ("Feast of Emptiness", 2),
    119331: ("It Will Be Written", 4),
    119332: ("Because of You", 4),
    119333: ("Boundless Feeling", 4),
    119334: ("Dreamful Gold", 4),
    119335: ("Falling in Past Light", 4),
    119336: ("An Old Pal's Legacy", 4),
    119337: ("Empty Like Shala", 4),
    119338: ("Tsukimi Himiko", 4),
    119339: ("Out of Reach", 4),
    119340: ("Boundless Logos", 4),
    119341: ("The Lonely Moon", 4),
    119342: ("Hometown", 4),
    119343: ("Awakening", 4),
    119344: ("Proof of Good and Evil", 3),
    119345: ("Faraway Ship", 3),
    119346: ("Ravenous Gully", 3),
    119347: ("Grey-scale Rainbow", 3),
    119348: ("Nine Lives", 3),
    119349: ("Key to the Deep", 1),
}


# GENERIC


class Boss(APIModel, Unique):
    """Represents a Boss encountered in Abyss or Memorial Arena."""

    id: int
    name: str
    icon: str = Aliased("avatar")

    @pydantic.field_validator("icon")
    def __fix_url(cls, url: str) -> str:
        # I noticed that sometimes the urls are returned incorrectly, which appears to be
        # a problem on the hoyolab website too, so I expect this to be fixed sometime.
        # For now, this hotfix seems to work.
        return re.sub(r"/boss_\d+\.", lambda m: str.upper(m[0]), url, flags=re.IGNORECASE)


class ELF(APIModel, Unique):
    """Represents an ELF equipped for a battle."""

    id: int
    name: str
    icon: str = Aliased("avatar")
    rarity: str
    upgrade_level: int = Aliased("star")

    @pydantic.field_validator("rarity", mode="before")
    def __fix_rank(cls, rarity: typing.Union[int, str]) -> str:
        if isinstance(rarity, str):
            return rarity

        # ELFs come in rarities A and S, API returns 4 and 5, respectively
        return ["A", "S"][rarity - 4]


# ABYSS


def get_abyss_rank_mi18n(rank: int, tier: int) -> str:
    """Turn the rank returned by the API into the respective rank name displayed in-game."""
    if tier == 4:
        mod = ("1", "2_1", "2_2", "2_3", "3_1", "3_2", "3_3", "4", "5")[rank - 1]
    else:
        mod = str(rank)
    return f"bbs/level{mod}"


class BaseAbyss(APIModel):
    """Represents one cycle of abyss.

    (3 days per cycle, 2 cycles per week)
    """

    # somewhat feel like this is overkill

    raw_tier: int = Aliased("area")
    score: int
    lineup: typing.Sequence[battlesuit.Battlesuit]
    boss: Boss
    elf: typing.Optional[ELF]


class OldAbyss(BaseAbyss):
    """Represents once cycle of Quantum Singularis or Dirac Sea.

    Exclusive to players of level 80 and below.
    """

    end_time: datetime.datetime = Aliased("time_second")
    raw_type: str = Aliased("type")
    result: str = Aliased("reward_type")
    raw_rank: int = Aliased("level")

    @pydantic.field_validator("raw_rank", mode="before")
    def __normalize_level(cls, rank: str) -> int:
        # The latestOldAbyssReport endpoint returns ranks as D/C/B/A,
        # while newAbyssReport returns them as 1/2/3/4(/5) respectively.
        # Having them as ints at base seems more useful than strs.
        # (in-game, they use the same names (Sinful, Agony, etc.))
        if isinstance(rank, int):
            return rank

        return 69 - ord(rank)


class SuperstringAbyss(BaseAbyss):
    """Represents one cycle of Superstring Abyss, exclusive to players of level 81 and up."""

    # NOTE endpoint: game_record/honkai3rd/api/latestOldAbyssReport

    end_time: datetime.datetime = Aliased("updated_time_second")
    raw_tier: int = 4  # Not returned by API, always the case
    placement: int = Aliased("rank")
    trophies_gained: int = Aliased("settled_cup_number")
    end_trophies: int = Aliased("cup_number")
    raw_start_rank: int = Aliased("level")
    raw_end_rank: int = Aliased("settled_level")

    @property
    def start_trophies(self) -> int:
        return self.end_trophies - self.trophies_gained


# MEMORIAL ARENA


def prettify_MA_rank(rank: int) -> str:  # Independent of mi18n
    """Turn the rank returned by the API into the respective rank name displayed in-game."""
    brackets = (0, 0.20, 2, 7, 17, 35, 65, 100)
    return f"{brackets[rank - 1]:1.2f} ~ {brackets[rank]:1.2f}"


class MemorialBattle(APIModel):
    """Represents weekly performance against a single Memorial Arena boss."""

    score: int
    lineup: typing.Sequence[battlesuit.Battlesuit]
    elf: typing.Optional[ELF]
    boss: Boss


class MemorialArena(APIModel):
    """Represents aggregate weekly performance for the entire Memorial Arena rotation."""

    score: int
    ranking: float = Aliased("ranking_percentage")
    raw_rank: int = Aliased("rank")
    raw_tier: int = Aliased("area")
    end_time: datetime.datetime = Aliased("time_second")
    battle_data: typing.Sequence[MemorialBattle] = Aliased("battle_infos")

    @property
    def rank(self) -> str:
        """The user's Memorial Arena rank as displayed in-game."""
        return prettify_MA_rank(self.raw_rank)


# ELYSIAN REALMS
# TODO: Implement a way to link response_json["avatar_transcript"] data to be added to
#       ER lineup data; will require new Battlesuit subclass.


class Condition(APIModel):
    """Represents a debuff picked at the beginning of an Elysian Realms run."""

    name: str
    description: str = Aliased("desc")
    difficulty: int


class Signet(APIModel):
    """Represents a buff Signet picked in an Elysian Realms run."""

    id: int
    icon: str
    number: int

    @property
    def name(self) -> str:
        return [
            "Deliverance",
            "Gold",
            "Decimation",
            "Bodhi",
            "Setsuna",
            "Infinity",
            "Vicissitude",
            "Ego",
            "Unknown",      # Unused, no signet with id 9.
            "Discipline",   # icon 12
            "Helix",        # icon 13
            "Daybreak",     # icon 9
            "Stars",        # icon 10
            "Reverie",      # icon 11
        ][self.id - 1]  # fmt: skip

    def get_scaled_icon(self, scale: typing.Literal[1, 2, 3] = 2) -> str:
        if not 1 <= scale <= 3:
            raise ValueError("Scale must lie between 1 and 3.")

        return self.icon.replace("@2x", "" if scale == 1 else f"@{scale}x")


class RemembranceSigil(APIModel):
    """Represents a Remembrance Sigil from Elysian Realms."""

    icon: str

    @property
    def id(self) -> int:
        match = re.match(r".*/(\d+).png", self.icon)
        return int(match[1]) if match else 0

    @property
    def name(self) -> str:
        sigil = REMEMBRANCE_SIGILS.get(self.id)
        return sigil[0] if sigil else "Unknown"

    @property
    def rarity(self) -> int:
        sigil = REMEMBRANCE_SIGILS.get(self.id)
        return sigil[1] if sigil else 1


class ElysianRealm(APIModel):
    """Represents one completed run of Elysean Realms."""

    completed_at: datetime.datetime = Aliased("settle_time_second")
    floors_cleared: int = Aliased("level")
    score: int
    difficulty: int = Aliased("punish_level")
    conditions: typing.Sequence[Condition]
    signets: typing.Sequence[Signet] = Aliased("buffs")
    leader: battlesuit.Battlesuit = Aliased("main_avatar")
    supports: typing.Sequence[battlesuit.Battlesuit] = Aliased("support_avatars")
    elf: typing.Optional[ELF]
    remembrance_sigil: RemembranceSigil = Aliased("extra_item_icon")

    @pydantic.field_validator("remembrance_sigil", mode="before")
    def __extend_sigil(cls, sigil: typing.Any) -> typing.Any:
        if isinstance(sigil, str):
            return dict(icon=sigil)

        return sigil

    @property
    def lineup(self) -> typing.Sequence[battlesuit.Battlesuit]:
        return [self.leader, *self.supports]
