from typing import Any, Dict, Generic, List, TypeVar

from pydantic import Field
from pydantic.generics import GenericModel

from genshin import models

__all__ = ["RecordCardData", "BaseRecordCardSetting", "BaseRecordCard"]


class RecordCardData(models.APIModel):
    """Represents a data entry of a record card"""

    name: str
    value: str


class BaseRecordCardSetting(models.APIModel):
    """Represents a privacy setting of a record card"""

    _names: dict[int, str] = {}

    id: int = Field(galias="switch_id")
    description: str = Field(galias="switch_name")
    public: bool = Field(galias="is_public")

    @property
    def name(self) -> str:
        return self._names.get(self.id, "")


# Allow for subclasses of RecordCard to use subclasses of RecordCardSetting without mypy acting up
# Is there really no better way to do this?
RecordCardSettingT = TypeVar("RecordCardSettingT", bound=BaseRecordCardSetting)


# Can probably leave this one unexposed through __all__? Don't think users will ever need this.
class GenericRecordCard(models.GameAccount, GenericModel, Generic[RecordCardSettingT]):
    """Represents a hoyolab record card containing very basic user info"""

    game_id: int
    uid: int = Field(galias="game_role_id")

    data: List[RecordCardData]
    privacy_settings: List[RecordCardSettingT] = Field(galias="data_switches")

    # unknown meaning
    background_image: str
    has_uid: bool = Field(galias="has_role")
    public: bool = Field(galias="is_public")

    @property
    def game(self):
        return {
            1: models.Game.honkai,
            2: models.Game.genshin,
        }[self.game_id]

    def as_dict(self) -> Dict[str, Any]:
        """Helper function which turns fields into properly named ones"""
        return {d.name: (int(d.value) if d.value.isdigit() else d.value) for d in self.data}


# Could be helpful in case a new game gets full hoyolab support and we don't handle it (yet?)
class BaseRecordCard(GenericRecordCard[BaseRecordCardSetting]):
    """Represents a hoyolab record card containing very basic user info for an unknown game"""
