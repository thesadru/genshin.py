"""Search logfile for authkeys."""
import os
import re
import typing
import urllib.parse

from genshin.utility import fs

__all__ = ["get_logfile", "extract_authkey", "get_authkey", "get_banner_ids"]

AUTHKEY_FILE = os.path.join(fs.get_tempdir(), "genshin_authkey.txt")


def get_logfile() -> typing.Optional[str]:
    """Find a Genshin Impact logfile."""
    mihoyo_dir = os.path.expanduser("~/AppData/LocalLow/miHoYo/")
    for name in ["Genshin Impact", "原神", "YuanShen"]:
        output_log = os.path.join(mihoyo_dir, name, "output_log.txt")
        if os.path.isfile(output_log):
            return output_log

    return None  # no genshin installation


def _read_logfile(logfile: typing.Optional[str] = None) -> str:
    """Return the contents of a logfile."""
    logfile = logfile or get_logfile()
    if logfile is None:
        raise FileNotFoundError("No Genshin Installation was found, could not get gacha data.")
    with open(logfile) as file:
        return file.read()


def extract_authkey(string: str) -> typing.Optional[str]:
    """Extract an authkey from the provided string."""
    match = re.search(r"https://.+?authkey=([^&#]+)", string, re.MULTILINE)
    if match is not None:
        return urllib.parse.unquote(match.group(1))
    return None


def get_authkey(logfile: typing.Optional[str] = None) -> str:
    """Get an authkey contained in a logfile."""
    authkey = extract_authkey(_read_logfile(logfile))
    if authkey is not None:
        with open(AUTHKEY_FILE, "w") as file:
            file.write(authkey)
        return authkey

    # otherwise try the tempfile (may be expired!)
    if os.path.isfile(AUTHKEY_FILE):
        with open(AUTHKEY_FILE) as file:
            return file.read()

    raise ValueError(
        "No authkey could be found in the logs or in a tempfile. "
        "Open the history in-game first before attempting to request it."
    )


def get_banner_ids(logfile: typing.Optional[str] = None) -> typing.Sequence[str]:
    """Get all banner ids from a log file."""
    log = _read_logfile(logfile)
    ids = re.findall(r"OnGetWebViewPageFinish:https://.+?gacha_id=([^&#]+)", log)
    return list(set(ids))
