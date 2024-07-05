import enum
import typing

from genshin.models.model import Aliased, APIModel, Unique

__all__ = (
    "ZZZBaseAgent",
    "ZZZElementType",
    "ZZZPartialAgent",
    "ZZZSpeciality",
)


class ZZZElementType(enum.IntEnum):
    """ZZZ element type."""

    PHYSICAL = 200
    FIRE = 201
    ICE = 202
    ELECTRIC = 203
    ETHER = 205


class ZZZSpeciality(enum.IntEnum):
    """ZZZ agent compatible speciality."""

    ATTACK = 1
    STUN = 2
    ANOMALY = 3
    SUPPORT = 4
    DEFENSE = 5


class ZZZBaseAgent(APIModel, Unique):
    """ZZZ base agent model."""

    id: int  # 4 digit number
    element: ZZZElementType = Aliased("element_type")
    rarity: typing.Literal["S", "A"]
    name: str = Aliased("name_mi18n")
    speciality: ZZZSpeciality = Aliased("avatar_profession")
    faction_icon: str = Aliased("group_icon_path")
    flat_icon: str = Aliased("hollow_icon_path")

    @property
    def icon(self) -> str:
        return (
            f"https://act-webstatic.hoyoverse.com/game_record/zzz/role_square_avatar/role_square_avatar_{self.id}.png"
        )


class ZZZPartialAgent(ZZZBaseAgent):
    """Character without any equipment."""

    level: int
    rank: int
    """Also known as Mindscape Cinema in-game."""
