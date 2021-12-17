import pytest

from genshin import GenshinClient


@pytest.mark.asyncio
async def test_calculator_characters(client: GenshinClient):
    characters = await client.get_calculator_characters()
    characters.sort(key=lambda c: c.id)

    assert len(characters) >= 43

    character = characters[0]
    assert character.name == "Kamisato Ayaka"
    assert "genshin" in character.icon
    assert character.max_level == 90
    assert character.level == 1
    assert not character.collab


@pytest.mark.asyncio
async def test_calculator_weapons(client: GenshinClient):
    weapons = await client.get_calculator_weapons()
    weapons.sort(key=lambda w: w.id)

    assert len(weapons) >= 126

    weapon = weapons[0]
    assert weapon.name == "Dull Blade"
    assert weapon.max_level == 70
    assert weapon.level == 1


@pytest.mark.asyncio
async def test_calculator_artifacts(client: GenshinClient):
    artifacts = await client.get_calculator_artifacts()
    artifacts.sort(key=lambda a: a.id)

    assert len(artifacts) >= 69

    artifact = artifacts[0]
    assert artifact.name == "Heart of Comradeship"
    assert artifact.max_level == 12
    assert artifact.level == 1


@pytest.mark.asyncio
async def test_character_talents(client: GenshinClient):
    talents = await client.get_character_talents(10000002)
    talents.sort(key=lambda t: t.group_id)

    # special character - has dash
    # fmt: off
    assert len(talents) == 7
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


@pytest.mark.asyncio
async def test_complete_artifact_set(client: GenshinClient):
    artifact_id = 7554  # Gladiator's Nostalgia (feather / pos #1)

    artifacts = await client.get_complete_artifact_set(artifact_id)
    artifacts.sort(key=lambda x: x.pos)

    assert len(artifacts) == 4
    assert artifact_id not in (a.id for a in artifacts)

    assert artifacts[0].id == 7552 and artifacts[0].name == "Gladiator's Destiny"
    assert artifacts[1].id == 7555 and artifacts[1].name == "Gladiator's Longing"
    assert artifacts[2].id == 7551 and artifacts[2].name == "Gladiator's Intoxication"
    assert artifacts[3].id == 7553 and artifacts[3].name == "Gladiator's Triumphus"


@pytest.mark.asyncio
async def test_calculate(client: GenshinClient):
    cost = await client.calculate(
        character=(10000052, 1, 90),  # Raiden Shogun
        weapon=(11509, 1, 90),  # Mistsplitter Reforged
        artifacts={
            # Emblem of Severed Fate
            9651: (0, 20),  # goblet 4
            9652: (0, 20),  # plume 2
            9653: (0, 20),  # circlet 5
            9654: (0, 20),  # flower 1
            9655: (0, 20),  # sands 3
        },
        talents={
            5231: (1, 10),  # attack
            5232: (1, 10),  # skill
            5239: (1, 10),  # burst
        },
    )

    assert len(cost.character) == 11
    assert len(cost.weapon) == 12
    assert len(cost.artifacts) == 5 and all(len(i.list) == 2 for i in cost.artifacts)
    assert len(cost.talents) == 9
    assert len(cost.total) == 25
    assert cost.total[0].name == "Mora" and cost.total[0].amount == 9_533_850


# TODO: Tests with synced calculation data
