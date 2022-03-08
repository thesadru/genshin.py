"""Private and confidential models.

All models will lack private data by design.
"""

from genshin.models.model import APIModel

__all__ = ["AccountInfo"]


class AccountInfo(APIModel):
    """Account info."""

    account_id: int
    account_name: str
    weblogin_token: str

    @property
    def login_ticket(self) -> str:
        return self.weblogin_token
