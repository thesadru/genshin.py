"""HSR Lineup Simulator."""

import typing

import pydantic

from genshin.models.model import APIModel, Aliased
from . import character


class StarRailGameModeFloor(APIModel):
    """A floor of a game mode, like MOC Stage 1."""

    id: int
    name: str
    floor: int

    @pydantic.model_validator(mode="before")
    @classmethod
    def __extract_floor(cls, v: dict[str, typing.Any]) -> dict[str, typing.Any]:
        extend = v["extend"]
        v["floor"] = extend["floor"]
        return v


class StarRailGameMode(APIModel):
    """HSR game mode, like MOC."""

    id: int
    name: str
    floors: list[StarRailGameModeFloor]

    @pydantic.model_validator(mode="before")
    @classmethod
    def __unnest_children(cls, v: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Unnest the children field."""
        if not (children := v.get("children")):
            msg = "Missing 'children' field in HSRGameMode."
            raise ValueError(msg)

        v["floors"] = children[0]["children"]
        v["name"] = children[0]["name"]
        return v


class StarRailLineup(APIModel):
    """A HSR lineup."""

    id: str
    uid: str = Aliased("account_uid")
    nickname: str
    avatar_url: str

    title: str
    characters: list[list[character.StarRailLineupCharacter]] = Aliased("avatar_group")

    @pydantic.field_validator("characters", mode="before")
    @classmethod
    def __unnest_characters(cls, v: list[dict[str, typing.Any]]) -> list[list[dict[str, typing.Any]]]:
        return [g["avatar_details"] for g in v]


class StarRailLineupResponse(APIModel):
    """Response for HSR lineups."""

    lineups: list[StarRailLineup] = Aliased("list")
    next_page_token: str
