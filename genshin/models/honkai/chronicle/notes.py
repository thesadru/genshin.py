import typing

import pydantic

from genshin.models.model import TZDateTime

__all__ = ("BattleField", "GodWar", "GreedyEndless", "HonkaiNotes", "UltraEndless")


class HonkaiNotesEvent(pydantic.BaseModel):
    """Base event model."""

    end_time: TZDateTime = pydantic.Field(alias="schedule_end")
    is_open: bool


class GreedyEndless(HonkaiNotesEvent):
    """Greedy Endless event model."""

    current_reward: int = pydantic.Field(alias="cur_reward")
    max_reward: int


class UltraEndless(HonkaiNotesEvent):
    """Ultra Endless event model."""

    group_level: int
    challenge_score: int


class BattleField(HonkaiNotesEvent):
    """Battle Field event model."""

    current_reward: int = pydantic.Field(alias="cur_reward")
    max_reward: int
    current_sss_reward: int = pydantic.Field(alias="cur_sss_reward")
    max_sss_reward: int


class GodWar(HonkaiNotesEvent):
    """God War event model."""

    current_reward: int = pydantic.Field(alias="cur_reward")
    max_reward: int


class HonkaiNotes(pydantic.BaseModel):
    """Honkai Impact 3rd real-time notes model."""

    current_stamina: int
    max_stamina: int
    stamina_recover_time: int
    current_train_score: int

    greedy_endless: GreedyEndless
    ultra_endless: UltraEndless
    battle_field: typing.Optional[BattleField] = None
    god_war: GodWar
