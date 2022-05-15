"""Search logfile for authkeys."""
import pathlib
import re
import typing
import urllib.parse

from genshin.utility import fs

__all__ = ["extract_authkey", "get_authkey", "get_banner_ids"]

PathLike = typing.Union[str, pathlib.Path]

AUTHKEY_FILE = fs.get_tempdir() / "genshin_authkey.txt"


def get_logfile() -> typing.Optional[pathlib.Path]:
    """Find a Genshin Impact logfile."""
    mihoyo_dir = pathlib.Path("~/AppData/LocalLow/miHoYo/").expanduser()
    for name in ("Genshin Impact", "原神", "YuanShen"):
        output_log = mihoyo_dir / name / "output_log.txt"
        if output_log.is_file():
            return output_log

    return None  # no genshin installation


def _read_logfile(logfile: typing.Optional[PathLike] = None) -> str:
    """Return the contents of a logfile."""
    if isinstance(logfile, str):
        logfile = pathlib.Path(logfile)

    logfile = logfile or get_logfile()
    if logfile is None:
        raise FileNotFoundError("No Genshin Installation was found, could not get gacha data.")

    return logfile.read_text()


def extract_authkey(string: str) -> typing.Optional[str]:
    """Extract an authkey from the provided string."""
    match = re.search(r"https://.+?authkey=([^&#]+)", string, re.MULTILINE)
    if match is not None:
        return urllib.parse.unquote(match.group(1))
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
