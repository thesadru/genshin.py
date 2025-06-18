"""Errors received from the API."""

import typing

from genshin.constants import GEETEST_RETCODES

__all__ = [
    "ERRORS",
    "AccountMuted",
    "AccountNotFound",
    "AlreadyClaimed",
    "AuthkeyException",
    "AuthkeyTimeout",
    "CookieException",
    "DailyGeetestTriggered",
    "DataNotPublic",
    "GeetestError",
    "GenshinException",
    "InvalidAuthkey",
    "InvalidCookies",
    "RedemptionClaimed",
    "RedemptionCooldown",
    "RedemptionException",
    "RedemptionInvalid",
    "TooManyRequests",
    "check_for_geetest",
    "raise_for_retcode",
]


class GenshinException(Exception):
    """A base genshin exception."""

    retcode: int = 0
    original: str = ""
    msg: str = ""

    def __init__(
        self, response: typing.Optional[typing.Mapping[str, typing.Any]] = None, msg: typing.Optional[str] = None
    ) -> None:
        response = response or {}

        self.retcode = response.get("retcode", self.retcode)
        self.original = response.get("message", "")
        self.msg = msg or self.msg or self.original

        if self.retcode and f"[{self.retcode}]" not in self.msg:
            msg = f"[{self.retcode}] {self.msg}"
        else:
            msg = self.msg

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


class InternalDatabaseError(GenshinException):
    """Internal database error."""

    retcode = -1


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

    retcode = -100
    msg = "Cookies are not valid."


class TooManyRequests(CookieException):
    """Made too many requests and got ratelimited."""

    retcode = 10101
    msg = "Cannot get data for more than 30 accounts per cookie per day."


class VisitsTooFrequently(GenshinException):
    """Visited a page too frequently.

    Must be handled with exponential backoff.
    """

    retcode = -110
    msg = "Visits too frequently."


class AlreadyClaimed(GenshinException):
    """Already claimed the daily reward today."""

    retcode = -5003
    msg = "Already claimed the daily reward today."


class DailyGeetestTriggered(GenshinException):
    """Geetest triggered during daily reward claim."""

    msg = "Geetest triggered during daily reward claim."

    gt: str
    challenge: str

    def __init__(self, response: typing.Mapping[str, typing.Any], *, gt: str, challenge: str) -> None:
        self.gt = gt
        self.challenge = challenge

        super().__init__(response)


class AuthkeyException(GenshinException):
    """Base error for authkeys."""


class InvalidAuthkey(AuthkeyException):
    """Authkey is not valid."""

    retcode = -100
    msg = "Authkey is not valid."


class AuthkeyTimeout(AuthkeyException):
    """Authkey has timed out."""

    retcode = -101
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


class RedeemGameLevelTooLow(RedemptionException):
    """Redemption code cannot be claimed because the game level is too low."""


class AccountLoginFail(GenshinException):
    """Account if not exists in hoyoverse (Or password incorrect)."""

    msg = "Account login failed."


class AccountHasLocked(GenshinException):
    """Account has logged incorrect over than 3 - 5 time(s). It's will be locked and wait 20 minute."""

    msg = "Account has been locked because exceeded password limit. Please wait 20 minute and try again"


class WrongOTP(GenshinException):
    """Wrong OTP code."""

    msg = "The provided OTP code is wrong."


class GeetestError(GenshinException):
    """Geetest triggered during the battle chronicle API request."""

    def __init__(self, response: dict[str, typing.Any]) -> None:
        super().__init__(response)

    msg = "Geetest triggered during the battle chronicle API request."


class OTPRateLimited(GenshinException):
    """Too many OTP messages sent for the number.

    The limit is 40 messages/day/number.
    """

    retcode = -119
    msg = "Too many OTP messages sent for the number."


class IncorrectGameAccount(GenshinException):
    """Game account is incorrect."""

    retcode = -216
    msg = "Game account is incorrect."


class IncorrectGamePassword(GenshinException):
    """Game password is incorrect."""

    retcode = -202
    msg = "Game password is incorrect."


class AccountDoesNotExist(GenshinException):
    """Account does not exist."""

    retcode = -3203
    msg = "Account does not exist."


class VerificationCodeRateLimited(GenshinException):
    """Too many verification code requests for the account."""

    retcode = -3206
    msg = "Too many verification code requests for the account."


class AccountMuted(GenshinException):
    """Account is muted."""

    retcode = 2010
    msg = "Account is muted."


class ActionInCooldown(GenshinException):
    """Action is in cooldown."""


class NoNeedGeetest(GenshinException):
    """No need to do geetest."""


_TGE = type[GenshinException]
_errors: dict[int, typing.Union[_TGE, str, tuple[_TGE, typing.Optional[str]]]] = {
    # misc hoyolab
    -100: InvalidCookies,
    -108: "Invalid language.",
    -110: VisitsTooFrequently,
    1028: VisitsTooFrequently,
    2010: AccountMuted,
    # game record
    10001: InvalidCookies,
    -10001: "Malformed request.",
    -10002: "No game account associated with cookies.",
    # database game record
    10101: TooManyRequests,
    10102: DataNotPublic,
    10103: (InvalidCookies, "Cookies are valid but do not have a hoyolab account bound to them."),
    10104: "Cannot view real-time notes of other users.",
    # calculator
    -500001: "Invalid fields in calculation.",
    -500004: VisitsTooFrequently,
    -502001: "User does not have this character.",
    -502002: "Calculator sync is not enabled.",
    # mixin
    -1: InternalDatabaseError,
    10307: InternalDatabaseError,
    1009: AccountNotFound,
    # redemption
    -1065: RedemptionInvalid,
    -1071: InvalidCookies,
    -1073: (AccountNotFound, "Account has no game account bound to it."),
    -2001: (RedemptionInvalid, "Redemption code has expired."),
    -2003: (RedemptionInvalid, "Redemption code is incorrectly formatted."),
    -2004: RedemptionInvalid,
    -2006: (RedemptionInvalid, "Redemption code has reached max usage limit."),
    -2014: (RedemptionInvalid, "Redemption code not activated"),
    -2016: RedemptionCooldown,
    -2017: RedemptionClaimed,
    -2018: RedemptionClaimed,
    -2021: RedeemGameLevelTooLow,
    -2011: RedeemGameLevelTooLow,
    # rewards
    -5003: AlreadyClaimed,
    # chinese
    1008: AccountNotFound,
    -1104: "This action must be done in the app.",
    # account
    -3004: AccountLoginFail,
    -3208: AccountLoginFail,
    -3202: AccountHasLocked,
    -3203: AccountDoesNotExist,
    -3205: WrongOTP,
    -3206: VerificationCodeRateLimited,
    -3102: WrongOTP,
    # Miyoushe
    -119: OTPRateLimited,
    -3006: "Request too frequent.",  # OTP endpoint
    # Game login
    -216: IncorrectGameAccount,
    -202: IncorrectGamePassword,
    # lineup
    -1004: ActionInCooldown,
    -3101: ActionInCooldown,
    # geetest
    30001: NoNeedGeetest,
}

ERRORS: dict[int, tuple[_TGE, typing.Optional[str]]] = {
    retcode: (GenshinException, exc) if isinstance(exc, str) else exc if isinstance(exc, tuple) else (exc, None)
    for retcode, exc in _errors.items()
}


def raise_for_retcode(data: dict[str, typing.Any]) -> typing.NoReturn:
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

    if r in ERRORS:
        exctype, msg = ERRORS[r]
        raise exctype(data, m or msg)

    if "redemption" in m:
        raise RedemptionException(data)

    raise GenshinException(data)


def check_for_geetest(data: dict[str, typing.Any]) -> None:
    """Check if geetest was triggered during the request and raise an error if so."""
    retcode = data.get("retcode")
    if retcode is not None and retcode in GEETEST_RETCODES:
        raise GeetestError(data)

    if not data.get("data"):  # if is an error
        return

    gt_result = data["data"].get("gt_result", data["data"])

    if (
        gt_result.get("risk_code") != 0
        and gt_result.get("gt")
        and gt_result.get("challenge")
        and gt_result.get("success") != 0
    ):
        raise DailyGeetestTriggered(data, gt=gt_result.get("gt"), challenge=gt_result.get("challenge"))
