import genshin


def test_character_icon():
    i = genshin.models.genshin.CharacterIcon(10000002)

    base = "https://upload-os-bbs.mihoyo.com/game_record/genshin/"
    assert i.icon == base + "character_icon/UI_AvatarIcon_Ayaka.png"
    assert i.image == base + "character_image/UI_AvatarIcon_Ayaka@2x.png"
    assert i.side_icon == base + "character_side_icon/UI_AvatarIcon_Side_Ayaka.png"


def test_base_character():
    char = genshin.models.genshin.BaseCharacter(id=10000002)
    assert char.name == "Kamisato Ayaka"
    assert char.element == "Cryo"
    assert char.rarity == 5

    char = genshin.models.genshin.BaseCharacter(name="Aloy")
    assert char.name == "Aloy"
    assert char.rarity == 5
    assert char.collab

    url = "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Kazuha.png"
    char = genshin.models.genshin.BaseCharacter(icon=url)
    assert char.name == "Kaedehara Kazuha"
