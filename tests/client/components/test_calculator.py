import genshin


async def test_calculator_characters(client: genshin.Client):
    characters = await client.get_calculator_characters()
    assert len(characters) >= 43

    character = min(characters, key=lambda character: character.id)
    assert character.name == "Kamisato Ayaka"
    assert "enka.network" in character.icon
    assert character.max_level == 90
    assert character.level == 0
    assert not character.collab


async def test_calculator_weapons(client: genshin.Client):
    weapons = await client.get_calculator_weapons()
    assert len(weapons) >= 126

    weapon = min(weapons, key=lambda weapon: weapon.id)
    assert weapon.name == "Dull Blade"
    assert weapon.max_level == 70
    assert weapon.level == 0


async def test_calculator_artifacts(client: genshin.Client):
    artifacts = await client.get_calculator_artifacts()
    assert len(artifacts) >= 69

    artifact = min(artifacts, key=lambda artifact: artifact.id)
    assert artifact.name == "Labyrinth Wayfarer"
    assert artifact.max_level == 16
    assert artifact.level == 0


async def test_calculator_furnishings(client: genshin.Client):
    furnishings = await client.get_calculator_furnishings()
    assert len(furnishings) >= 100

    furnishing = min(furnishings, key=lambda furnishing: furnishing.id)
    assert furnishing.name == "Timber Wall With Jade Eaves"


# noqa: PT018
async def test_character_talents(client: genshin.Client):
    talents = await client.get_character_talents(10000002)
    assert len(talents) == 7

    talents = sorted(talents, key=lambda t: t.group_id)

    # special character - has dash
    # fmt: off
    assert talents[0].type == "passive" and talents[0].name == "Amatsumi Kunitsumi Sanctification"
    assert talents[1].type == "passive" and talents[1].name == "Kanten Senmyou Blessing"
    assert talents[2].type == "passive" and talents[2].name == "Fruits of Shinsa"
    assert talents[3].type == "attack"  and talents[3].name == "Normal Attack: Kamisato Art - Kabuki"
    assert talents[4].type == "skill"   and talents[4].name == "Kamisato Art: Hyouka"
    assert talents[5].type == "dash"    and talents[5].name == "Kamisato Art: Senho"
    assert talents[6].type == "burst"   and talents[6].name == "Kamisato Art: Soumetsu"
    # fmt: on

    assert talents[0].max_level == 1
    assert talents[6].max_level == 10


# noqa: PT018
async def test_complete_artifact_set(client: genshin.Client):
    artifact_id = 7554  # Gladiator's Nostalgia (feather / pos #1)

    artifacts = await client.get_complete_artifact_set(artifact_id)
    artifacts = sorted(artifacts, key=lambda artifact: artifact.pos)

    assert len(artifacts) == 4
    assert artifact_id not in (a.id for a in artifacts)

    assert artifacts[0].id == 7552 and artifacts[0].name == "Gladiator's Destiny"
    assert artifacts[1].id == 7555 and artifacts[1].name == "Gladiator's Longing"
    assert artifacts[2].id == 7551 and artifacts[2].name == "Gladiator's Intoxication"
    assert artifacts[3].id == 7553 and artifacts[3].name == "Gladiator's Triumphus"


async def test_calculate(client: genshin.Client):
    cost = await (
        client.calculator()
        .set_character(10000052, current=1, target=90)
        .set_weapon(11509, current=1, target=90)
        .set_artifact_set(9651, current=0, target=20)
        .with_current_talents(current=1, target=10)
    )

    assert len(cost.character) == 11
    assert len(cost.weapon) == 12
    assert len(cost.artifacts) == 5 and all(len(i.list) == 2 for i in cost.artifacts)
    assert len(cost.talents) == 9
    assert len(cost.total) == 25
    assert cost.total[0].name == "Hero's Wit"


async def test_furnishing_calculate(client: genshin.Client):
    cost = await client.furnishings_calculator().add_furnishing(363106)

    assert cost.total[0].name == "Iron Chunk" and cost.total[0].amount == 6
    assert cost.total[1].name == "White Iron Chunk" and cost.total[1].amount == 6


async def test_calculator_characters_synced(lclient: genshin.Client):
    characters = await lclient.get_calculator_characters(sync=True)
    assert characters[0].level != 0


async def test_character_details(lclient: genshin.Client):
    # Amber
    details = await lclient.get_character_details(10000021)
    assert details.weapon.level >= 1
