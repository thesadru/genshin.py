"""Genshin chronicle character."""
import enum
import typing

if typing.TYPE_CHECKING:
    import pydantic.v1 as pydantic
else:
    try:
        import pydantic.v1 as pydantic
    except ImportError:
        import pydantic

from genshin.models.genshin import character
from genshin.models.model import Aliased, APIModel, Unique

__all__ = [
    "Artifact",
    "ArtifactSet",
    "ArtifactSetEffect",
    "Character",
    "CharacterWeapon",
    "Constellation",
    "Outfit",
    "PartialCharacter",
    "PropertyType",
    "PropertyValue",
    "DetailCharacterWeapon",
    "ArtifactProperty",
    "DetailArtifact",
    "SkillAffix",
    "CharacterSkill",
    "GenshinDetailCharacter",
    "GenshinDetailCharacters",
    "GenshinWeaponType"
]


class GenshinWeaponType(enum.IntEnum):
    """Character weapon types."""

    SWORD = 1
    CATALYST = 10
    CLAYMORE = 11
    BOW = 12
    POLEARM = 13


class PartialCharacter(character.BaseCharacter):
    """Character without any equipment."""

    level: int
    friendship: int = Aliased("fetter")
    constellation: int = Aliased("actived_constellation_num")


class CharacterWeapon(APIModel, Unique):
    """Character's equipped weapon."""

    id: int
    icon: str
    name: str
    rarity: int
    description: str = Aliased("desc")
    level: int
    type: str = Aliased("type_name")
    ascension: int = Aliased("promote_level")
    refinement: int = Aliased("affix_level")


class ArtifactSetEffect(APIModel):
    """Effect of an artifact set."""

    pieces: int = Aliased("activation_number")
    effect: str
    enabled: bool = False

    class Config:
        # this is for the "enabled" field, hopefully nobody abuses this
        allow_mutation = True


class ArtifactSet(APIModel, Unique):
    """Artifact set."""

    id: int
    name: str
    effects: typing.Sequence[ArtifactSetEffect] = Aliased("affixes")


class Artifact(APIModel, Unique):
    """Character's equipped artifact."""

    id: int
    icon: str
    name: str
    pos_name: str
    pos: int
    rarity: int
    level: int
    set: ArtifactSet


class Constellation(APIModel, Unique):
    """Character constellation."""

    id: int
    icon: str
    pos: int
    name: str
    effect: str
    activated: bool = Aliased("is_actived")

    @property
    def scaling(self) -> bool:
        """Whether the constellation is simply for talent scaling"""
        return "U" in self.icon


class Outfit(APIModel, Unique):
    """Outfit of a character."""

    id: int
    icon: str
    name: str


class Character(PartialCharacter):
    """Character with equipment."""

    weapon: CharacterWeapon
    artifacts: typing.Sequence[Artifact] = Aliased("reliquaries")
    constellations: typing.Sequence[Constellation]
    outfits: typing.Sequence[Outfit] = Aliased("costumes")

    @pydantic.validator("artifacts")
    def __add_artifact_effect_enabled(cls, artifacts: typing.Sequence[Artifact]) -> typing.Sequence[Artifact]:
        sets: typing.Dict[int, typing.List[Artifact]] = {}
        for arti in artifacts:
            sets.setdefault(arti.set.id, []).append(arti)

        for artifact in artifacts:
            for effect in artifact.set.effects:
                if effect.pieces <= len(sets[artifact.set.id]):
                    effect.enabled = True

        return artifacts


class PropertyType(APIModel):
    """A property such as Crit Rate, HP, HP%."""

    property_type: int
    name: str
    icon: typing.Optional[str]
    filter_name: str

    @pydantic.root_validator(pre=True)
    def __fix_names(cls, values: typing.Mapping[str, typing.Any]) -> typing.Mapping[str, typing.Any]:
        """Fix "\xa0" in Crit Damage + Crit Rate names."""
        name = values.get("name")
        filter_name = values.get("filter_name")

        return {**values, "name": name.replace(u"\xa0", " "), "filter_name": filter_name.replace(u"\xa0", " ")}


class PropertyValue(APIModel):
    """A property with a value."""
    base: str
    add: str
    final: str
    info: PropertyType


class DetailCharacterWeapon(CharacterWeapon):
    """Detailed Genshin Weapon with main/sub stats."""
    main_property: PropertyValue
    sub_property: typing.Optional[PropertyValue]


class ArtifactProperty(APIModel):
    value: str
    times: int
    info: PropertyType


class DetailArtifact(Artifact):
    main_property: ArtifactProperty
    sub_properties: typing.Sequence[ArtifactProperty] = Aliased("sub_property_list")


class SkillAffix(APIModel):
    name: str
    value: str


class CharacterSkill(APIModel):
    id: int = Aliased("skill_id")
    skill_type: int
    name: str
    level: int

    description: str = Aliased("desc")
    affixes: typing.Sequence[SkillAffix] = Aliased("skill_affix_list")
    icon: str
    is_unlocked: bool = Aliased("is_unlock")


class GenshinDetailCharacter(PartialCharacter):
    """Full Detailed Genshin Character"""
    is_chosen: bool

    # display_image is a different image that is returned by the full character endpoint, but it is not the full gacha art.
    display_image: str = Aliased("image")

    weapon_type: GenshinWeaponType
    weapon: DetailCharacterWeapon

    costumes: typing.Sequence[Outfit]

    artifacts: typing.Sequence[DetailArtifact] = Aliased("relics")
    constellations: typing.Sequence[Constellation]

    skills: typing.Sequence[CharacterSkill]

    selected_properties: typing.Sequence[PropertyValue]
    base_properties: typing.Sequence[PropertyValue]
    extra_properties: typing.Sequence[PropertyValue]
    element_properties: typing.Sequence[PropertyValue]


class GenshinDetailCharacters(APIModel):
    """Genshin character list."""

    avatars: typing.Sequence[GenshinDetailCharacter] = Aliased("list")

    property_map: typing.Mapping[str, PropertyType]
    artifact_property_options: typing.Mapping[str, typing.Sequence[PropertyType]] = Aliased("relic_property_options")

    artifact_wiki: typing.Mapping[str, str] = Aliased("relic_wiki")
    weapon_wiki: typing.Mapping[str, str]
    avatar_wiki: typing.Mapping[str, str]

    @pydantic.root_validator(pre=True)
    def __fill_additional_fields(cls, values: typing.Mapping[str, typing.Any]) -> typing.Mapping[str, typing.Any]:
        """Fill additional fields for convenience."""
        relic_property_options = values.get("artifact_property_options", {})
        property_map = values.get("property_map", {})
        characters = values.get("avatars", [])

        # Map properties to artifacts
        for relic_type, properties in relic_property_options.items():
            formatted_properties = []
            for prop in properties:
                prop = property_map.get(str(prop), {})
                formatted_properties.append(prop)
            relic_property_options[relic_type] = formatted_properties

        for char in characters:
            # Extract character info from .base
            for key, value in char["base"].items():
                if key == "weapon":  # Ignore .weapon in base as it does not have full info.
                    continue
                char[key] = value

            # Map properties to main/sub stat for weapon.
            main_property = char["weapon"]["main_property"]
            char["weapon"]["main_property"]["info"] = property_map.get(str(main_property["property_type"]), {})
            if sub_property := char["weapon"]["sub_property"]:
                char["weapon"]["sub_property"]["info"] = property_map.get(str(sub_property["property_type"]), {})

            # Map properties to artifacts
            for artifact in char["relics"]:
                main_property = artifact["main_property"]
                artifact["main_property"]["info"] = property_map.get(str(main_property["property_type"]), {})
                for sub_property in artifact["sub_property_list"]:
                    sub_property["info"] = property_map.get(str(sub_property["property_type"]), {})

            # Map character properties
            for prop in char['base_properties'] + char['selected_properties'] + char['extra_properties'] + char['element_properties']:
                prop['info'] = property_map.get(str(prop['property_type']), {})

        return values
