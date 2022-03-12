"""API routes."""
import itertools
import typing

import yarl

from genshin import types

__all__ = [
    "CALCULATOR_URL",
    "DETAIL_LEDGER_URL",
    "GACHA_INFO_URL",
    "INFO_LEDGER_URL",
    "RECORD_URL",
    "REWARD_URL",
    "Route",
    "TAKUMI_URL",
    "WEBSTATIC_URL",
    "YSULOG_URL",
]


class Route:
    """A route which provides useful metadata."""

    universal: typing.Optional[yarl.URL] = None
    urls: typing.Mapping[types.Region, yarl.URL]

    def __init__(self, overseas: str, chinese: typing.Optional[str] = None) -> None:
        if not chinese:
            self.universal = yarl.URL(overseas)
            self.urls = {}
        else:
            self.urls = {
                types.Region.OVERSEAS: yarl.URL(overseas),
                types.Region.CHINESE: yarl.URL(chinese),
            }

    @property
    def needs_authkey(self) -> bool:
        """Whether this route requires an authkey."""
        for url in itertools.chain(self.urls.values(), [self.universal]):
            if "gacha" in str(url) or "log" in str(url):
                return True

        return False

    def get_url(self, region: typing.Optional[types.Region] = None) -> yarl.URL:
        """Attempt to get a URL."""
        if region is None:
            if self.universal is None:
                raise ValueError("Region must be provided for this Route.")

            return self.universal

        if region in self.urls:
            if not self.urls[region]:
                raise RuntimeError(f"URL does not support {region.name} region.")

            return self.urls[region]

        raise TypeError(f"Could not find URL for {region.name}.")


WEBSTATIC_URL = Route("https://webstatic-sea.hoyoverse.com/")

TAKUMI_URL = Route(
    "https://api-os-takumi.mihoyo.com/",
    "https://api-takumi.mihoyo.com/",
)
RECORD_URL = Route(
    "https://bbs-api-os.hoyolab.com/game_record/",
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

CALCULATOR_URL = Route(
    "https://sg-public-api.hoyoverse.com/event/calculateos/",
    "",
)

REWARD_URL = Route(
    "https://hk4e-api-os.hoyoverse.com/event/sol/",
    "https://api-takumi.mihoyo.com/event/bbs_sign_reward/",
)

GACHA_INFO_URL = Route(
    "https://hk4e-api-os.hoyoverse.com/event/gacha_info/api/",
    "https://hk4e-api.mihoyo.com/event/gacha_info/api",
)
YSULOG_URL = Route(
    "https://hk4e-api-os.hoyoverse.com/ysulog/api/",
    "",
)
