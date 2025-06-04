"""HSR Lineup Simulator."""

import typing
import pydantic


class HSRGameModeFloor(pydantic.BaseModel):
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


class HSRGameMode(pydantic.BaseModel):
    """HSR game mode, like MOC."""

    id: int
    name: str
    floors: list[HSRGameModeFloor]

    @pydantic.model_validator(mode="before")
    @classmethod
    def __unnest_children(cls, v: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Unnest the children field."""
        if not (children := v.get("children")):
            msg = "Missing 'children' field in HSRGameMode."
            raise ValueError(msg)

        v["floors"] = children[0]["children"]
        return v

class HSRLineup(pydantic.BaseModel):
    """A HSR lineup."""
    
    id: str
    uid: str = pydantic.Field(alias="account_uid")
    nickname: str
    avatar_url: str
    
    title: str