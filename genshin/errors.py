from typing import Any, Dict

__all__ = [
    "GenshinException",
    # game record:
    "AccountNotFound",
    "DataNotPublic",
    # cookies:
    "CookieException",
    "InvalidCookies",
    "TooManyRequests",
    # authkeys:
    "AuthkeyException",
    "InvalidAuthkey",
    "AuthkeyTimeout",
]


class GenshinException(Exception):
    """A base genshin exception"""

    retcode: int
    original: str

    def __init__(self, response: Dict[str, Any], msg: str = None) -> None:
        self.retcode = response.get("retcode", 0)
        self.original = response.get("message", "")

        if msg is None:
            msg = f"[{self.retcode}] {self.original}"
        else:
            msg = f"[{self.retcode}] {msg}"

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
