"""API routes."""
import abc
import typing

import yarl

from genshin import types

__all__ = [
    "CALCULATOR_URL",
    "COMMUNITY_URL",
    "DETAIL_LEDGER_URL",
    "GACHA_INFO_URL",
    "INFO_LEDGER_URL",
    "LINEUP_URL",
    "MI18N",
    "RECORD_URL",
    "REWARD_URL",
    "Route",
    "TAKUMI_URL",
    "WEBSTATIC_URL",
    "YSULOG_URL",
]


class BaseRoute(abc.ABC):
    """A route which provides useful metadata."""


class Route(BaseRoute):
    """Standard route."""

    url: yarl.URL

    def __init__(self, url: str) -> None:
        self.url = yarl.URL(url)

    def get_url(self) -> yarl.URL:
        """Attempt to get a URL."""
        return self.url


class InternationalRoute(BaseRoute):
    """Standard international route."""

    urls: typing.Mapping[types.Region, yarl.URL]

    def __init__(self, overseas: str, chinese: str) -> None:
        self.urls = {
            types.Region.OVERSEAS: yarl.URL(overseas),
            types.Region.CHINESE: yarl.URL(chinese),
        }

    def get_url(self, region: types.Region) -> yarl.URL:
        """Attempt to get a URL."""
        if not self.urls[region]:
            raise RuntimeError(f"URL does not support {region.name} region.")

        return self.urls[region]


class GameRoute(BaseRoute):
    """Standard international game URL."""

    urls: typing.Mapping[types.Region, typing.Mapping[types.Game, yarl.URL]]

    def __init__(
        self,
        overseas: typing.Mapping[str, str],
        chinese: typing.Mapping[str, str],
    ) -> None:
        self.urls = {
            types.Region.OVERSEAS: {types.Game(game): yarl.URL(url) for game, url in overseas.items()},
            types.Region.CHINESE: {types.Game(game): yarl.URL(url) for game, url in chinese.items()},
        }

    def get_url(self, region: types.Region, game: types.Game) -> yarl.URL:
        """Attempt to get a URL."""
        if not self.urls[region]:
            raise RuntimeError(f"URL does not support {region.name} region.")

        if not self.urls[region][game]:
            raise RuntimeError(f"URL does not support {game.name} game for {region.name} region.")

        return self.urls[region][game]


WEBSTATIC_URL = Route("https://webstatic-sea.hoyoverse.com/")

TAKUMI_URL = InternationalRoute(
    overseas="https://api-os-takumi.mihoyo.com/",
    chinese="https://api-takumi.mihoyo.com/",
)
COMMUNITY_URL = InternationalRoute(
    overseas="https://bbs-api-os.hoyolab.com/community/apihub/",
    chinese="https://api-takumi-record.mihoyo.com/community/apihub/",
)
RECORD_URL = InternationalRoute(
    overseas="https://bbs-api-os.hoyolab.com/game_record/",
    chinese="https://api-takumi-record.mihoyo.com/game_record/app/",
)
LINEUP_URL = InternationalRoute(
    overseas="https://sg-public-api.hoyoverse.com/event/simulatoros/",
    chinese="",
)

INFO_LEDGER_URL = InternationalRoute(
    overseas="https://hk4e-api-os.hoyoverse.com/event/ysledgeros/month_info",
    chinese="https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo",
)
DETAIL_LEDGER_URL = InternationalRoute(
    overseas="https://hk4e-api-os.hoyoverse.com/event/ysledgeros/month_detail",
    chinese="https://hk4e-api.mihoyo.com/event/ys_ledger/monthDetail",
)

CALCULATOR_URL = InternationalRoute(
    overseas="https://sg-public-api.hoyoverse.com/event/calculateos/",
    chinese="https://api-takumi.mihoyo.com/event/e20200928calculate/v1/",
)

WIKI_URL = Route("https://sg-wiki-api.hoyolab.com/hoyowiki/wapi")

REWARD_URL = GameRoute(
    overseas=dict(
        genshin="https://sg-hk4e-api.hoyolab.com/event/sol?act_id=e202102251931481",
        honkai3rd="https://sg-public-api.hoyolab.com/event/mani?act_id=e202110291205111",
    ),
    chinese=dict(
        genshin="https://api-takumi.mihoyo.com/event/bbs_sign_reward/?act_id=e202009291139501",
        honkai3rd="",
    ),
)

CODE_URL = Route("https://sg-hk4e-api.hoyoverse.com/common/apicdkey/api/webExchangeCdkey")

GACHA_INFO_URL = InternationalRoute(
    overseas="https://hk4e-api-os.hoyoverse.com/event/gacha_info/api/",
    chinese="https://hk4e-api.mihoyo.com/event/gacha_info/api",
)
YSULOG_URL = InternationalRoute(
    overseas="https://hk4e-api-os.hoyoverse.com/ysulog/api/",
    chinese="",
)

MI18N = dict(
    bbs="https://webstatic-sea.mihoyo.com/admin/mi18n/bbs_cn/m11241040191111/m11241040191111-{lang}.json",
    inquiry="https://mi18n-os.hoyoverse.com/webstatic/admin/mi18n/hk4e_global/m02251421001311/m02251421001311-{lang}.json",
)
