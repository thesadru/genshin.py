import typing
from enum import Enum

from genshin.models.model import Aliased, APIModel, TZDateTime

__all__ = (
    "IncomeData",
    "PolychromeIncome",
    "PolychromeIncomeType",
    "ZZZCurrencyType",
    "ZZZDiary",
    "ZZZDiaryDetail",
    "ZZZDiaryDetailItem",
    "ZZZDiaryPlayerInfo",
    "ZZZIncomeCurrency",
)


class PolychromeIncomeType(Enum):
    """Polychrome income type enum."""

    DAILY = "daily_activity_rewards"
    DEVELOPMENT = "growth_rewards"
    SHIYU_DEFENSE = "shiyu_rewards"
    MAIL = "mail_rewards"
    HOLLOW_ZERO = "hollow_rewards"
    EVENT = "event_rewards"
    OTHER = "other_rewards"


class PolychromeIncome(APIModel):
    """Polychrome income model."""

    source: PolychromeIncomeType = Aliased("action")
    num: int
    percent: int


class ZZZCurrencyType(Enum):
    """Currency type enum."""

    POLYCHROME = "PolychromesData"
    MASTER_TAPE = "MatserTapeData"
    BOOPONS = "BooponsData"


class ZZZIncomeCurrency(APIModel):
    """Currency model."""

    type: ZZZCurrencyType = Aliased("data_type")
    num: int = Aliased("count")
    name: str = Aliased("data_name")


class IncomeData(APIModel):
    """Income model."""

    currencies: typing.Sequence[ZZZIncomeCurrency] = Aliased("list")
    polychrome_incomes: typing.Sequence[PolychromeIncome] = Aliased("income_components")


class ZZZDiaryPlayerInfo(APIModel):
    """Player info model."""

    nickname: str
    avatar_url: str = Aliased("avatar")


class ZZZDiary(APIModel):
    """ZZZ monthly earnings model."""

    uid: int
    region: str
    current_month: str
    data_month: str

    income: IncomeData = Aliased("month_data")
    month_options: typing.Sequence[str] = Aliased("optional_month")
    player: ZZZDiaryPlayerInfo = Aliased("role_info")


class ZZZDiaryDetailItem(APIModel):
    """ZZZ monthly earning detail item model."""

    id: str
    source: PolychromeIncomeType = Aliased("action")
    time: TZDateTime
    num: int


class ZZZDiaryDetail(APIModel):
    """ZZZ monthly earning detail model."""

    uid: int
    region: str
    data_month: str
    current_page: int
    total: int
    items: typing.Sequence[ZZZDiaryDetailItem] = Aliased("list")

    currency_name: str = Aliased("data_name")
    currency_type: ZZZCurrencyType = Aliased("data_type")
