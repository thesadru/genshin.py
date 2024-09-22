"""Transaction client."""

import functools
import typing
import urllib.parse

from genshin import paginators, utility
from genshin.client import routes
from genshin.client.components import base
from genshin.models.genshin import transaction as models

__all__ = ["TransactionClient"]


class TransactionClient(base.BaseClient):
    """Transaction component."""

    async def request_transaction(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the transaction log endpoint."""
        params = dict(params or {})
        authkey = authkey or self.authkey

        if authkey is None:
            raise RuntimeError("No authkey provided")

        base_url = routes.YSULOG_URL.get_url(self.region)
        url = base_url / endpoint

        params["authkey_ver"] = 1
        params["sign_type"] = 2
        params["authkey"] = urllib.parse.unquote(authkey)
        params["lang"] = utility.create_short_lang_code(lang or self.lang)

        return await self.request(url, method=method, params=params, **kwargs)

    async def _get_transaction_page(
        self,
        end_id: int,
        kind: str,
        *,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
    ) -> typing.Sequence[models.BaseTransaction]:
        """Get a single page of transactions."""
        kind = models.TransactionKind(kind)
        endpoint = "Get" + kind.value.capitalize() + "Log"

        data = await self.request_transaction(
            endpoint,
            lang=lang,
            authkey=authkey,
            params=dict(end_id=end_id, size=20),
        )

        transactions: list[models.BaseTransaction] = []
        for trans in data["list"]:
            model = models.ItemTransaction if "name" in trans else models.Transaction
            model = typing.cast("type[models.BaseTransaction]", model)
            transactions.append(model(**trans, kind=kind))

        return transactions

    def transaction_log(
        self,
        kind: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
        *,
        limit: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
        authkey: typing.Optional[str] = None,
        end_id: int = 0,
    ) -> paginators.Paginator[models.BaseTransaction]:
        """Get the transaction log of a user."""
        kinds = kind or ["primogem", "crystal", "resin", "artifact", "weapon"]

        if isinstance(kinds, str):
            kinds = [kinds]

        iterators: list[paginators.Paginator[models.BaseTransaction]] = []
        for kind in kinds:
            iterators.append(
                paginators.CursorPaginator(
                    functools.partial(
                        self._get_transaction_page,
                        kind=kind,
                        lang=lang,
                        authkey=authkey,
                    ),
                    limit=limit,
                    end_id=end_id,
                )
            )

        if len(iterators) == 1:
            return iterators[0]

        return paginators.MergedPaginator(iterators, key=lambda trans: trans.time.timestamp())
