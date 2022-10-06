"""Search logfile for authkeys."""
import pathlib
import re
import typing
import urllib.parse

from genshin.utility import fs

__all__ = ["extract_authkey", "get_authkey", "get_banner_ids"]

PathLike = typing.Union[str, pathlib.Path]

AUTHKEY_FILE = fs.get_tempdir() / "genshin_authkey.txt"


def get_datafile(game_location: typing.Optional[PathLike] = None) -> typing.Optional[pathlib.Path]:
    """Find a Genshin Impact datafile."""
    # C:\Program Files\Genshin Impact\Genshin Impact game\GenshinImpact_Data
    # C:\Program Files\Genshin Impact\Genshin Impact game\YuanShen_Data
    if game_location:
        game_location = pathlib.Path(game_location)
        if game_location.is_file():
            return game_location

        for name in ("Genshin Impact game/GenshinImpact_Data", "Genshin Impact game/YuanShen_Data"):
            data_location = game_location / name / "webCaches/Cache/Cache_Data/data_2"
            if data_location.is_file():
                return data_location

        raise FileNotFoundError("No data file found in the provided game location.")

    mihoyo_dir = pathlib.Path("~/AppData/LocalLow/miHoYo/").expanduser()

    for name in ("Genshin Impact", "原神"):
        output_log = mihoyo_dir / name / "output_log.txt"
        if not output_log.is_file():
            continue  # wrong language

        logfile = output_log.read_text()
        match = re.search(r"Warmup file (.+?_Data)", logfile, re.MULTILINE)
        if match is None:
            return None  # no genshin installation location in logfile

        data_location = pathlib.Path(f"{match[1]}/webCaches/Cache/Cache_Data/data_2")
        if data_location.is_file():
            return data_location

        return None  # data location is improper

    return None  # no genshin datafile


def _read_datafile(game_location: typing.Optional[PathLike] = None) -> str:
    """Return the contents of a datafile."""
    datafile = get_datafile(game_location)
    if datafile is None:
        raise FileNotFoundError(
            "No Genshin Installation was found, could not get gacha data. "
            "Please check if you set correct game location."
        )

    try:
        # won't work if genshin is running or script using this function isn't run as administrator
        return datafile.read_text(errors="replace")
    except PermissionError as ex:
        raise PermissionError("Pleas turn off genshin impact or try running script as administrator!") from ex


def extract_authkey(string: str) -> typing.Optional[str]:
    """Extract an authkey from the provided string."""
    match = re.findall(r"https://.+?authkey=([^&#]+)&game_biz=", string, re.MULTILINE)
    if not match:
        return urllib.parse.unquote(match[-1])

    return None


def get_authkey(game_location: typing.Optional[PathLike] = None) -> str:
    """Get an authkey contained in a datafile."""
    authkey = extract_authkey(_read_datafile(game_location))
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
    log = _read_datafile(logfile)
    ids = re.findall(r"OnGetWebViewPageFinish:https://.+?gacha_id=([^&#]+)", log)
    return list(set(ids))
