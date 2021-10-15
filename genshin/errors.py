from typing import Any, Dict, NoReturn

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
    "raise_for_retcode",
]


class GenshinException(Exception):
    """A base genshin exception"""

    retcode: int
    original: str
    msg: str

    def __init__(self, response: Dict[str, Any], msg: str = None) -> None:
        self.retcode = response.get("retcode", 0)
        self.original = response.get("message", "")
        self.msg = msg or self.original

        if self.retcode:
            msg = f"[{self.retcode}] {self.msg}"

        super().__init__(msg)


class AccountNotFound(GenshinException):
    """Tried to get data with an invalid uid."""

    def __init__(self, response: Dict[str, Any], msg: str = None) -> None:
        super().__init__(response, msg or "Could not find user; uid may not be valid.")


class DataNotPublic(GenshinException):
    """User hasn't set their data to public."""

    def __init__(self, response: Dict[str, Any], msg: str = None) -> None:
        super().__init__(response, msg or "User's data is not public")


class CookieException(GenshinException):
    """Base error for cookies"""


class InvalidCookies(CookieException):
    """Cookies weren't valid"""


class TooManyRequests(CookieException):
    """Made too many requests and got ratelimited"""

    def __init__(self, response: Dict[str, Any], msg: str = None) -> None:
        msg = msg or "Cannnot get data for more than 30 accounts per cookie per day."
        super().__init__(response, msg)


class AlreadyClaimed(GenshinException):
    """Already claimed the daily reward today"""

    def __init__(self, response: Dict[str, Any], msg: str = None) -> None:
        super().__init__(response, msg or "Already claimed the daily reward today.")


class AuthkeyException(GenshinException):
    """Base error for authkeys"""

    def __init__(self, response: Dict[str, Any], msg: str = None) -> None:
        super().__init__(response, msg)


class InvalidAuthkey(AuthkeyException):
    """Authkey is not valid"""

    def __init__(self, response: Dict[str, Any]) -> None:
        super().__init__(response, "Authkey is not valid")


class AuthkeyTimeout(AuthkeyException):
    """Authkey is not valid"""

    def __init__(self, response: Dict[str, Any]) -> None:
        super().__init__(response, "Authkey is not valid")


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
    r, m = data["retcode"], data["message"]

    if m == "authkey error":
        if r == -100:
            raise InvalidAuthkey(data)
        elif r == -101:
            raise AuthkeyTimeout(data)
        else:
            raise AuthkeyException(data)

    if r == -100:
        raise InvalidCookies(data, "Cookies are not valid")
    elif r == -108:
        raise GenshinException(data, "Invalid language")

    elif r == 10001:
        raise InvalidCookies(data, "Cookies are not valid")
    elif r == -10001:
        raise GenshinException(data, "Malformed request")
    elif r == -10002:
        raise GenshinException(data, "No genshin account associated with cookies")

    elif r == 10101:
        raise TooManyRequests(data)
    elif r == 10102:
        raise DataNotPublic(data)
    elif r == 10103:
        msg = "Cookies are valid but do not have a hoyolab account bound to them"
        raise InvalidCookies(data, msg)

    elif r == -1:
        raise GenshinException(data, "Malformed request, maybe uid is invalid?")
    elif r == 1009:
        raise AccountNotFound(data)

    elif r == -1071:
        raise InvalidCookies(data)
    elif r == -1073:
        msg = "Cannot claim code. Account has no game account bound to it."
        raise GenshinException(data, msg)
    elif r == -2001:
        raise GenshinException(data, "Redemption code has expired.")
    elif r == -2003:
        raise GenshinException(data, "Invalid redemption code")
    elif r == -2017:
        raise GenshinException(data, "Redemption code has been claimed already.")
    elif r == -2021:
        msg = "Cannot claim codes for account with adventure rank lower than 10."
        raise GenshinException(data, msg)

    elif r == -5003:
        raise AlreadyClaimed(data, "Already claimed the daily reward today.")

    else:
        raise GenshinException(data)
