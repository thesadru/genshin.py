import warnings
from typing import TYPE_CHECKING

import genshin.client.genshin.base as genshin_base
from genshin.client import adapter, base


class BaseOverseasGenshinClient(genshin_base.BaseGenshinClient):
    DS_SALT = "6cqshh5dhw73bzxn20oexa9k516chk7s"
    ACT_ID = "e202102251931481"

    INFO_LEDGER_URL = "https://hk4e-api-os.mihoyo.com/event/ysledgeros/month_info"
    DETAIL_LEDGER_URL = "https://hk4e-api-os.mihoyo.com/event/ysledgeros/month_detail"
    CALCULATOR_URL = "https://sg-public-api.mihoyo.com/event/calculateos/"
    GACHA_INFO_URL = "https://hk4e-api-os.mihoyo.com/event/gacha_info/api/"
    YSULOG_URL = "https://hk4e-api-os.mihoyo.com/ysulog/api/"
    MAP_URL = "https://api-os-takumi-static.mihoyo.com/common/map_user/ys_obc/v1/map/"
    STATIC_MAP_URL = "https://api-os-takumi-static.mihoyo.com/common/map_user/ys_obc/v1/map"


class OverseasGenshinClient(BaseOverseasGenshinClient, adapter.Adapter):
    """Standard implementation of an overseas genshin client"""


class MultiCookieOverseasGenshinClient(genshin_base.BaseGenshinClient, adapter.MultiCookieAdapter):
    """Multi-Cookie implementation of an overseas genshin client"""


if not TYPE_CHECKING:

    class MultiCookieClient(MultiCookieOverseasGenshinClient):
        def __new__(cls):
            warnings.warn("MultiCookieClient has been renamed to MultiCookieGenshinClient", DeprecationWarning)
            return super().__new__(cls)


GenshinClient = OverseasGenshinClient
MultiCookieGenshinClient = MultiCookieOverseasGenshinClient
