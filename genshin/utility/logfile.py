"""Search logfile for authkeys."""
import pathlib
import re
import typing
from urllib.parse import unquote

from genshin.utility import fs

__all__ = ["extract_authkey", "get_authkey", "get_banner_ids"]

PathLike = typing.Union[str, pathlib.Path]

AUTHKEY_FILE = fs.get_tempdir() / "genshin_authkey.txt"
GAME_LOCATION = fs.get_tempdir() / "genshin_location.txt"


def set_geme_location(location: PathLike) -> None:
    """Set game directory for searching for logfile."""
    game_dir = pathlib.Path(location).expanduser()
    # Probably it's different for Chinese version
    log = game_dir / "Genshin Impact game" / "GenshinImpact_Data" / "webCaches" / "Cache" / "Cache_Data" / "data_2"
    if log.is_file():
        GAME_LOCATION.write_text(str(location))
    else:
        raise FileNotFoundError(
            "Incorrect game location, remember to set it before \"Genshin Impact game\" folder!"
        )


def get_logfile() -> typing.Optional[pathlib.Path]:
    """Find a Genshin Impact logfile."""
    if GAME_LOCATION.exists() is False or GAME_LOCATION.read_text() == "":
        output_log = pathlib.Path(
            "C:/Program Files/Genshin Impact/Genshin Impact game/GenshinImpact_Data/webCaches/Cache/Cache_Data/data_2"
        )
    else:
        output_log = pathlib.Path(
            f"{GAME_LOCATION.read_text()}/Genshin Impact game/GenshinImpact_Data/webCaches/Cache/Cache_Data/data_2"
        )
    if output_log.is_file():
        return output_log

    return None  # no genshin installation


def _read_logfile(logfile: typing.Optional[PathLike] = None) -> str:
    """Return the contents of a logfile."""
    if isinstance(logfile, str):
        logfile = pathlib.Path(logfile)

    logfile = logfile or get_logfile()
    if logfile is None:
        raise FileNotFoundError(
            "No Genshin Installation was found, could not get gacha data."
            "Pleas set game location using genshin.utility.logfile.set_geme_location(game location)"
        )

    try:
        # won't work if genshin is running or script using this function is run as administrator
        return logfile.read_text(errors='replace')
    except PermissionError as ex:
        raise PermissionError(
            "Pleas turn off genshin impact or try running script as administrator!"
        ) from ex


def extract_authkey(string: str) -> typing.Optional[str]:
    """Extract an authkey from the provided string."""
    match = re.search(
        r"https://webstatic-sea.hoyoverse.com/genshin/event/e20190909gacha-v2.+?authkey=([^&#]+)",
        string,
        re.MULTILINE
    )
    if match is not None:
        return unquote(match.group(1))
    return None


def get_authkey(logfile: typing.Optional[PathLike] = None) -> str:
    """Get an authkey contained in a logfile."""
    authkey = extract_authkey(_read_logfile(logfile))
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


def get_banner_ids(logfile: typing.Optional[PathLike] = None) -> typing.Sequence[str]:
    """Get all banner ids from a log file."""
    log = _read_logfile(logfile)
    ids = re.findall(r"OnGetWebViewPageFinish:https://.+?gacha_id=([^&#]+)", log)
    return list(set(ids))
