"""Search logfile for authkeys."""
import pathlib
import re
import typing
import urllib.parse

from genshin.utility import fs

__all__ = ["extract_authkey", "get_authkey", "get_banner_ids"]

PathLike = typing.Union[str, pathlib.Path]

AUTHKEY_FILE = fs.get_tempdir() / "genshin_authkey.txt"


def get_logfile(game_location: typing.Optional[PathLike] = None) -> typing.Optional[pathlib.Path]:
    """Find a Genshin Impact logfile."""
    if game_location is None:
        game_location = "C:/Program Files/Genshin Impact"

    for name in ("Genshin Impact", "原神", "YuanShen"):
        output_log = pathlib.Path(f"{game_location}/{name} game/{name.replace(' ', '')}_Data/webCaches/Cache/Cache_Data/data_2")
        if output_log.is_file():
            return output_log

    return None  # no genshin installation


def _read_logfile(game_location: typing.Optional[PathLike] = None) -> str:
    """Return the contents of a logfile."""
    logfile = get_logfile(game_location)
    if logfile is None:
        raise FileNotFoundError(
            "No Genshin Installation was found, could not get gacha data. "
            "Please check if you set correct game location."
        )

    try:
        # won't work if genshin is running or script using this function isn't run as administrator
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
        return urllib.parse.unquote(match.group(1))
    return None


def get_authkey(game_location: typing.Optional[PathLike] = None) -> str:
    """Get an authkey contained in a logfile."""
    authkey = extract_authkey(_read_logfile(game_location))
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
