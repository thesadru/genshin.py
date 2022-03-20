"""Errors received from the API."""
import typing

__all__ = [
    "AccountNotFound",
    "AlreadyClaimed",
    "AuthkeyException",
    "AuthkeyTimeout",
    "CookieException",
    "DataNotPublic",
    "ERRORS",
    "GenshinException",
    "InvalidAuthkey",
    "InvalidCookies",
    "RedemptionClaimed",
    "RedemptionCooldown",
    "RedemptionException",
    "RedemptionInvalid",
    "TooManyRequests",
    "raise_for_retcode",
]


class GenshinException(Exception):
    """A base genshin exception."""

    retcode: int
    original: str
    msg: str = ""

    def __init__(self, response: typing.Mapping[str, typing.Any], msg: typing.Optional[str] = None) -> None:
        self.retcode = response.get("retcode", 0)
        self.original = response.get("message", "")
        self.msg = msg or self.msg or self.original

        if self.retcode:
            msg = f"[{self.retcode}] {self.msg}"

        super().__init__(msg)

    def __repr__(self) -> str:
        response = {"retcode": self.retcode, "message": self.original}
        args = [repr(response)]
        if self.msg != self.original:
            args.append(repr(self.msg))

        return f"{type(self).__name__}({', '.join(args)})"

    @property
    def response(self) -> typing.Mapping[str, typing.Any]:
        return {"retcode": self.retcode, "message": self.original, "data": None}


class AccountNotFound(GenshinException):
    """Tried to get data with an invalid uid."""

    msg = "Could not find user; uid may be invalid."


class DataNotPublic(GenshinException):
    """User hasn't set their data to public."""

    msg = "User's data is not public."


class CookieException(GenshinException):
    """Base error for cookies."""


class InvalidCookies(CookieException):
    """Cookies weren't valid."""

    msg = "Cookies are not valid."


class TooManyRequests(CookieException):
    """Made too many requests and got ratelimited."""

    msg = "Cannot get data for more than 30 accounts per cookie per day."


class VisitsTooFrequently(GenshinException):
    """Visited a page too frequently.

    Must be handled with exponential backoff.
    """

    msg = "Visits too frequently."


class AlreadyClaimed(GenshinException):
    """Already claimed the daily reward today."""

    msg = "Already claimed the daily reward today."


class AuthkeyException(GenshinException):
    """Base error for authkeys."""


class InvalidAuthkey(AuthkeyException):
    """Authkey is not valid."""

    msg = "Authkey is not valid."


class AuthkeyTimeout(AuthkeyException):
    """Authkey has timed out."""

    msg = "Authkey has timed out."


class RedemptionException(GenshinException):
    """Exception caused by redeeming a code."""


class RedemptionInvalid(RedemptionException):
    """Invalid redemption code."""

    msg = "Invalid redemption code."


class RedemptionCooldown(RedemptionException):
    """Redemption is on cooldown."""

    msg = "Redemption is on cooldown."


class RedemptionClaimed(RedemptionException):
    """Redemption code has been claimed already."""

    msg = "Redemption code has been claimed already."


_TGE = typing.Type[GenshinException]
_errors: typing.Dict[int, typing.Union[_TGE, str, typing.Tuple[_TGE, typing.Optional[str]]]] = {
    # misc hoyolab
    -100: InvalidCookies,
    -108: "Invalid language.",
    -110: VisitsTooFrequently,
    # game record
    10001: InvalidCookies,
    -10001: "Malformed request.",
    -10002: "No genshin account associated with cookies.",
    # database game record
    10101: TooManyRequests,
    10102: DataNotPublic,
    10103: (InvalidCookies, "Cookies are valid but do not have a hoyolab account bound to them."),
    10104: "Tried to use a beta feature in an invalid context.",
    # calculator
    -500001: "Invalid fields in calculation.",
    -502001: "User does not have this character.",
    # mixin
    -1: "Internal database error.",
    1009: AccountNotFound,
    # redemption
    -1071: InvalidCookies,
    -1073: (AccountNotFound, "Account has no game account bound to it."),
    -2001: (RedemptionInvalid, "Redemption code has expired."),
    -2004: RedemptionInvalid,
    -2016: RedemptionCooldown,
    -2017: RedemptionClaimed,
    -2021: (RedemptionException, "Cannot claim codes for accounts with adventure rank lower than 10."),
    # rewards
    -5003: AlreadyClaimed,
    # chinese
    1008: AccountNotFound,
    -1104: "This action must be done in the app.",
}

ERRORS: typing.Dict[int, typing.Tuple[_TGE, typing.Optional[str]]] = {
    retcode: ((exc, None) if isinstance(exc, type) else (GenshinException, exc) if isinstance(exc, str) else exc)
    for retcode, exc in _errors.items()
}


def raise_for_retcode(data: typing.Dict[str, typing.Any]) -> typing.NoReturn:
    """Raise an equivalent error to a response.

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
    """
    r, m = data.get("retcode", 0), data.get("message", "")

    if m.startswith("authkey"):
        if r == -100:
            raise InvalidAuthkey(data)
        elif r == -101:
            raise AuthkeyTimeout(data)
        else:
            raise AuthkeyException(data)

    elif r in ERRORS:
        exctype, msg = ERRORS[r]
        raise exctype(data, msg)

    else:
        raise GenshinException(data)
