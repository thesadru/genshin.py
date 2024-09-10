"""Wiki component."""

import typing

from genshin import types
from genshin.client import cache, routes
from genshin.client.components import base
from genshin.models.genshin import wiki as models

__all__ = ["WikiClient"]


class WikiClient(base.BaseClient):
    """Wiki component."""

    async def request_wiki(
        self,
        endpoint: str,
        *,
        lang: typing.Optional[str] = None,
        headers: typing.Optional[typing.Mapping[str, str]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the wiki endpoint."""
        headers = dict(headers or {})

        url = routes.WIKI_URL.get_url() / endpoint
        headers["x-rpc-language"] = lang or self.lang

        return await self.request(url, headers=headers, **kwargs)

    @typing.overload
    async def get_wiki_previews(  # noqa: D102 missing docstring in overload?
        self,
        menu: typing.Literal[models.WikiPageType.CHARACTER],
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.CharacterPreview]: ...

    @typing.overload
    async def get_wiki_previews(  # noqa: D102 missing docstring in overload?
        self,
        menu: typing.Literal[models.WikiPageType.WEAPON],
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.WeaponPreview]: ...

    @typing.overload
    async def get_wiki_previews(  # noqa: D102 missing docstring in overload?
        self,
        menu: typing.Literal[models.WikiPageType.ARTIFACT],
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.ArtifactPreview]: ...

    @typing.overload
    async def get_wiki_previews(  # noqa: D102 missing docstring in overload?
        self,
        menu: typing.Literal[models.WikiPageType.ENEMY],
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.EnemyPreview]: ...

    @typing.overload
    async def get_wiki_previews(  # noqa: D102 missing docstring in overload?
        self,
        menu: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.BaseWikiPreview]: ...

    async def get_wiki_previews(
        self,
        menu: int,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.BaseWikiPreview]:
        """Get a list of wiki previews."""
        payload = dict(filters=[], menu_id=int(menu), page_num=1, page_size=1000, use_es=True)
        cache_key = cache.cache_key("wiki", endpoint="entry", menu=menu, lang=lang or self.lang)
        data = await self.request_wiki("get_entry_page_list", data=payload, lang=lang, static_cache=cache_key)

        cls = models._ENTRY_PAGE_MODELS.get(typing.cast(models.WikiPageType, menu), models.BaseWikiPreview)

        return [cls(**i) for i in data["list"] if i["icon_url"]]

    async def get_wiki_page(
        self,
        id: types.IDOr[models.BaseWikiPreview],
        *,
        lang: typing.Optional[str] = None,
    ) -> models.WikiPage:
        """Get a wiki page."""
        params = dict(entry_page_id=int(id))
        cache_key = cache.cache_key("wiki", endpoint="page", id=id, lang=lang or self.lang)
        data = await self.request_wiki("entry_page", lang=lang, params=params, static_cache=cache_key)

        data["page"].pop("lang", "")  # always an empty string
        return models.WikiPage(**data["page"])

    async def get_wiki_pages(
        self,
        ids: typing.Collection[types.IDOr[models.BaseWikiPreview]],
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.WikiPage]:
        """Get multiple wiki pages without modules."""
        payload = dict(entry_page_ids=[int(i) for i in ids])
        data = await self.request_wiki("entry_pages", lang=lang, data=payload)

        return [models.WikiPage(**i) for i in data["entry_pages"]]
