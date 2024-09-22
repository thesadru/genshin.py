"""Search logfile for authkeys."""

import pathlib
import re
import typing
import urllib.parse

from genshin import types
from genshin.utility import fs

__all__ = ["extract_authkey", "get_authkey", "get_genshin_banner_ids"]

PathLike = typing.Union[str, pathlib.Path]

AUTHKEY_FILE = fs.get_tempdir() / "genshin_authkey.txt"


# output_log
# ~/AppData/LocalLow/miHoYo/Genshin Impact/output_log.txt
# ~/AppData/LocalLow/miHoYo/原神/output_log.txt
# ~/AppData/LocalLow/Cognosphere/Star Rail/Player.log
# ~/AppData/LocalLow/miHoYo/崩坏：星穹铁道/output_log.txt
# data_2
# C:/Program Files/Genshin Impact/Genshin Impact game/GenshinImpact_Data/webCaches/2.16.0.0/Cache/Cache_Data/data_2
# C:/Program Files/Genshin Impact/Genshin Impact game/YuanShen_Data/webCaches/2.16.0.0/Cache/Cache_Data/data_2
# C:/Program Files/Star Rail/StarRail_Data/webCaches/2.15.0.0/Cache/Cache_Data/data_2
# C:/Program Files/Star Rail/StarRail_Data/webCaches/2.15.0.0/Cache/Cache_Data/data_2


def _search_output_log(content: str) -> pathlib.Path:
    """Search output log for data_2."""
    match = re.search(r"([A-Z]:/.*?/GenshinImpact_Data)", content, re.MULTILINE)
    match = match or re.search(r"([A-Z]:/.*?/YuanShen_Data)", content, re.MULTILINE)
    match = match or re.search(r"([A-Z]:/.*?/StarRail_Data)", content, re.MULTILINE)
    if match is None:
        raise FileNotFoundError("No Genshin/Star Rail installation location in logfile")

    base_dir = pathlib.Path(match[1]) / "webCaches"
    webCaches = [entry for entry in base_dir.iterdir() if entry.is_dir() and entry.name.startswith("2.")]

    data_location = max(webCaches, key=lambda x: x.name) / "Cache/Cache_Data/data_2"
    if data_location.is_file():
        return data_location

    raise FileNotFoundError("Genshin/Star Rail installation location is improper")


def get_output_log(*, game: typing.Optional[types.Game] = None) -> pathlib.Path:
    """Get output_log.txt for a game."""
    locallow = pathlib.Path("~/AppData/LocalLow").expanduser()

    game_name: list[str] = []
    if game is None or game == types.Game.GENSHIN:
        game_name += ["Genshin Impact", "原神"]
    if game is None or game == types.Game.STARRAIL:
        game_name += ["Star Rail", "崩坏：星穹铁道"]

    if not game_name:
        raise ValueError(f"Invalid game {game!r}.")

    for company_name in ("miHoYo", "HoYoverse", "Cognosphere"):
        for name in game_name:
            for file_name in ("Player.log", "output_log.txt"):
                output_log = locallow / company_name / name / file_name
                if output_log.is_file():
                    return output_log

    raise FileNotFoundError("No output log found.")


def _expand_game_location(game_location: pathlib.Path, *, game: typing.Optional[types.Game] = None) -> pathlib.Path:
    """Expand a game location folder to data_2."""
    data_location: list[pathlib.Path] = []
    if "Data" in str(game_location):
        while "Data" not in game_location.name:
            game_location = game_location.parent

        data_location = [game_location]
    else:
        if game is None or game == types.Game.GENSHIN:
            locations = ["Genshin Impact/Genshin Impact game", "Genshin Impact game"]
            data_names = ["GenshinImpact_Data", "YuanShen_Data"]
            data_location += [
                game_location / location / data_name for location in locations for data_name in data_names
            ]
        if game is None or game == types.Game.STARRAIL:
            locations = ["Star Rail", "Star Rail/Games", "Games", "崩坏：星穹铁道"]
            data_names = ["StarRail_Data"]
            data_location += [
                game_location / location / data_name for location in locations for data_name in data_names
            ]
        if not data_location:
            raise ValueError(f"Invalid game {game!r}.")

    for directory in data_location:
        if not directory.is_dir():
            continue

        base_dir = directory / "webCaches"
        webCaches = [entry for entry in base_dir.iterdir() if entry.is_dir() and entry.name.startswith("2.")]

        datafile = max(webCaches, key=lambda x: x.name) / "Cache/Cache_Data/data_2"
        if datafile.is_file():
            return datafile

    raise FileNotFoundError("No data file found in the provided game location.")


def get_datafile(
    game_location: typing.Optional[PathLike] = None, *, game: typing.Optional[types.Game] = None
) -> pathlib.Path:
    """Get data_2 for a game."""
    if game_location:
        return _expand_game_location(pathlib.Path(game_location), game=game)

    output_log = get_output_log(game=game)
    return _search_output_log(output_log.read_text())


def _read_datafile(game_location: typing.Optional[PathLike] = None, *, game: typing.Optional[types.Game] = None) -> str:
    """Return the contents of a datafile."""
    datafile = get_datafile(game_location, game=game)

    try:
        return datafile.read_text(errors="replace")
    except PermissionError as ex:
        raise PermissionError("Please turn off Genshin Impact/Star Rail or try running script as administrator") from ex


def extract_authkey(string: str) -> typing.Optional[str]:
    """Extract an authkey from the provided string."""
    match = re.findall(r"https://.+?authkey=([^&#]+)", string, re.MULTILINE)
    if match:
        return urllib.parse.unquote(match[-1])

    return None


def get_authkey(game_location: typing.Optional[PathLike] = None, *, game: typing.Optional[types.Game] = None) -> str:
    """Get an authkey contained in a datafile."""
    authkey = extract_authkey(_read_datafile(game_location, game=game))
    if authkey is not None:
        AUTHKEY_FILE.write_text(authkey)
        return authkey

    # otherwise try the tempfile (may be expired!)
    if AUTHKEY_FILE.is_file():
        return AUTHKEY_FILE.read_text()

    raise ValueError(
        "No authkey could be found in the logs or in a tempfile. "
        "Open the history in-game first before attempting to request it."
    )


def get_genshin_banner_ids(logfile: typing.Optional[PathLike] = None) -> typing.Sequence[str]:
    """Get all banner ids from a log file."""
    log = _read_datafile(logfile)
    ids = re.findall(r"https://.+?gacha_id=([^&#]+)", log, re.MULTILINE)
    return list(set(ids))
