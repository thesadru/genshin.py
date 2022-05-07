import genshin


async def test_wiki_previews(client: genshin.Client):
    preview = await client.get_wiki_previews(genshin.models.WikiPageType.CHARACTER)

    assert preview


async def test_wiki_page(client: genshin.Client):
    page = await client.get_wiki_page(10)

    assert page.modules["Attributes"]["list"][0]["key"] == "Name"
    assert page.modules["Attributes"]["list"][0]["value"] == ["Keqing"]
