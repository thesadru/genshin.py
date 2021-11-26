import pytest

import genshin


@pytest.mark.parametrize("uid,is_uid", [(710785423, True), (8366222, False)])
def test_genshin_uid(uid: int, is_uid: bool):
    assert genshin.is_genshin_uid(uid) == is_uid


@pytest.mark.parametrize(
    "uid,chinese",
    [
        ("cn_gf01", True),
        ("cn_qd01", True),
        ("123456789", True),
        (567890123, True),
        ("os_usa", False),
        ("os_asia", False),
        ("678901234", False),
        (890123456, False),
    ],
)
def test_is_chinese(uid: int, chinese: bool):
    assert genshin.is_chinese(uid) == chinese


@pytest.mark.parametrize(
    "id,result",
    [
        (10000002, genshin.models.base.BaseCharacter),  # ayaka
        (11101, genshin.models.character.Weapon),  # dull blade
        (2150011, genshin.models.character.ArtifactSet),  # gladiator's finale
        (75544, genshin.models.character.Artifact),  # gladiator's nostalgia (flower)
    ],
)
def test_recognize_id(id: int, result: genshin.models.base.GenshinModel):
    assert genshin.recognize_id(id) is result
