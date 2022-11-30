import genshin


async def test(client: genshin.Client):
    replicas = await client.teapot_replicas(limit=9)
    assert len(replicas) >= 9

    blueprint = replicas[0].blueprint

    furnishings = await client.get_teapot_replica_blueprint(blueprint.share_code, region=blueprint.region)
    assert len(furnishings) >= 10
