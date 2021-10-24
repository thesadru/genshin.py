"""Errors raised by genshin.py"""
from typing import Any, Dict, NoReturn, Optional, Tuple, Type, Union

__all__ = [
    "GenshinException",
    # game record:
    "AccountNotFound",
    "DataNotPublic",
    # cookies:
    "CookieException",
    "InvalidCookies",
    "TooManyRequests",
    # redemption:
    "AlreadyClaimed",
    # authkeys:
    "AuthkeyException",
    "InvalidAuthkey",
    "AuthkeyTimeout",
    # misc:
    "ERRORS",
    "raise_for_retcode",
]


class GenshinException(Exception):
    """A base genshin exception"""

    retcode: int
    original: str
    msg: str = ""

    def __init__(self, response: Dict[str, Any], msg: str = None) -> None:
        self.retcode = response.get("retcode", 0)
        self.original = response.get("message", "")
        self.msg = msg or self.msg or self.original

        if self.retcode:
            msg = f"[{self.retcode}] {self.msg}"

        super().__init__(msg)

    def __repr__(self) -> str:
        response = {"retcode": self.retcode, "message": self.original}
        return f"{type(self).__name__}({response}, {self.msg!r})"


class AccountNotFound(GenshinException):
    """Tried to get data with an invalid uid."""

    msg = "Could not find user; uid may be invalid."


class DataNotPublic(GenshinException):
    """User hasn't set their data to public."""

    msg = "User's data is not public"


class CookieException(GenshinException):
    """Base error for cookies"""


class InvalidCookies(CookieException):
    """Cookies weren't valid"""

    msg = "Cookies are not valid"


class TooManyRequests(CookieException):
    """Made too many requests and got ratelimited"""

    msg = "Cannnot get data for more than 30 accounts per cookie per day."


class AlreadyClaimed(GenshinException):
    """Already claimed the daily reward today"""

    msg = "Already claimed the daily reward today."


class AuthkeyException(GenshinException):
    """Base error for authkeys"""


class InvalidAuthkey(AuthkeyException):
    """Authkey is not valid"""

    msg = "Authkey is not valid."


class AuthkeyTimeout(AuthkeyException):
    """Authkey has timed out"""

    msg = "Authkey has timed out."


_errors: Dict[int, Union[Tuple[Type[GenshinException], Optional[str]], Type[GenshinException]]] = {
    # misc hoyolab
    -100: InvalidCookies,
    -108: (GenshinException, "Invalid language."),
    # game record
    10001: InvalidCookies,
    -10001: (GenshinException, "Malformed request."),
    -10002: (GenshinException, "No genshin account associated with cookies."),
    # database game record
    10101: TooManyRequests,
    10102: DataNotPublic,
    10103: (InvalidCookies, "Cookies are valid but do not have a hoyolab account bound to them."),
    10104: (GenshinException, "Tried to use a beta feature in an invalid context"),
    # mixin
    -1: (GenshinException, "Internal database error."),
    1009: AccountNotFound,
    # redemption
    -1071: InvalidCookies,
    -1073: (GenshinException, "Cannot claim code. Account has no game account bound to it."),
    -2001: (GenshinException, "Redemption code has expired."),
    -2003: (GenshinException, "Invalid redemption code."),
    -2017: (GenshinException, "Redeption code has been claimed already."),
    -2021: (GenshinException, "Cannot claim codes for account with adventure rank lower than 10."),
    # rewards
    -5003: (AlreadyClaimed, "Already claimed the daily reward today."),
    # chinese
    1008: AccountNotFound,
}

ERRORS: Dict[int, Tuple[Type[GenshinException], Optional[str]]] = {
    retcode: ((exc, None) if isinstance(exc, type) else exc) for retcode, exc in _errors.items()
}


def raise_for_retcode(data: Dict[str, Any]) -> NoReturn:
    """Raise an equivalent error to a response

    game record:
        10001 = invalid cookie
        101xx = generic errors

    authkey:
        -100 = invalid authkey
        -101 = authkey timed out

    code redemption:
        20xx = invalid code or state
        -107x = invalid cookies

    daily reward:
        -500x = already claimed the daily reward

    unknown:
        -1 = malformed request / account not found
        -100 = invalid cookies
        -108 = invalid language
        1009 = account not found

    """
    r, m = data.get("retcode", 0), data.get("message", "")

    if m.startswith("authkey"):
        if r == -100:
            raise InvalidAuthkey(data)
        elif r == -101:
            raise AuthkeyTimeout(data)
        else:
            raise AuthkeyException(data)

    elif m.startswith("character id"):
        char = m.split(":")[1].split()[0]
        raise GenshinException(data, f"User does not have a character with id {char}")

    elif r in ERRORS:
        exctype, msg = ERRORS[r]
        raise exctype(data, msg)

    else:
        raise GenshinException(data)
