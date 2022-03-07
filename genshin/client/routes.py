"""API routes."""
import typing

import yarl

from genshin import types

__all__ = [
    "Route",
    "WEBSTATIC_URL",
    "TAKUMI_URL",
    "RECORD_URL",
    "INFO_LEDGER_URL",
    "DETAIL_LEDGER_URL",
    "CALCULATOR_URL",
    "REWARD_URL",
    "GACHA_INFO_URL",
    "YSULOG_URL",
]

REGIONS = (types.Region.OVERSEAS, types.Region.CHINESE)


class Route:
    """A route which provides useful metadata."""

    urls: typing.Mapping[types.Region, yarl.URL]

    def __init__(self, url: str, *urls: str) -> None:
        if not urls:
            self.urls = {types.Region.UNKNOWN: yarl.URL(url)}
            return

        urls = (url,) + urls
        self.urls = {region: yarl.URL(url) for region, url in zip(REGIONS, urls)}

    @property
    def needs_authkey(self) -> bool:
        """Whether this route requires an authkey."""
        for url in self.urls.values():
            if "gacha" in str(url) or "log" in str(url):
                return True

        return False

    def get_url(self, region: types.Region = types.Region.UNKNOWN) -> yarl.URL:
        """Attempt to get a URL, fallback to UNKNOWN."""
        return self.urls.get(region, self.urls[types.Region.UNKNOWN])


WEBSTATIC_URL = Route("https://webstatic-sea.hoyoverse.com/")

TAKUMI_URL = Route(
    "https://api-os-takumi.mihoyo.com/",
    "https://api-takumi.mihoyo.com/",
)
RECORD_URL = Route(
    "https://bbs-api-os.hoyoverse.com/game_record/",
    "https://api-takumi-record.mihoyo.com/game_record/app/",
)

INFO_LEDGER_URL = Route(
    "https://hk4e-api-os.hoyoverse.com/event/ysledgeros/month_info",
    "https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo",
)
DETAIL_LEDGER_URL = Route(
    "https://hk4e-api-os.hoyoverse.com/event/ysledgeros/month_detail",
    "https://hk4e-api.mihoyo.com/event/ys_ledger/monthDetail",
)

CALCULATOR_URL = Route("https://sg-public-api.hoyoverse.com/event/calculateos/")

REWARD_URL = Route(
    "https://hk4e-api-os.hoyoverse.com/event/sol/",
    "https://api-takumi.mihoyo.com/event/bbs_sign_reward/",
)

GACHA_INFO_URL = Route(
    "https://hk4e-api-os.hoyoverse.com/event/gacha_info/api/",
    "https://hk4e-api.mihoyo.com/event/gacha_info/api",
)
YSULOG_URL = Route("https://hk4e-api-os.hoyoverse.com/ysulog/api/")
