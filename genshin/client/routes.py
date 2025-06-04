"""API routes."""

import abc
import typing

import yarl

from genshin import types

__all__ = [
    "ACCOUNT_URL",
    "APP_LOGIN_URL",
    "BBS_REFERER_URL",
    "BBS_URL",
    "CALCULATOR_URL",
    "CARD_WAPI_URL",
    "CHECK_QRCODE_URL",
    "CN_WEB_LOGIN_URL",
    "COMMUNITY_URL",
    "COOKIE_V2_REFRESH_URL",
    "CREATE_MMT_URL",
    "CREATE_QRCODE_URL",
    "DETAIL_LEDGER_URL",
    "GACHA_URL",
    "GET_COOKIE_TOKEN_BY_GAME_TOKEN_URL",
    "GET_FP_URL",
    "GET_STOKEN_BY_GAME_TOKEN_URL",
    "GET_USER_REGION_URL",
    "HK4E_URL",
    "HKRPG_URL",
    "INFO_LEDGER_URL",
    "LINEUP_URL",
    "NAP_URL",
    "RECORD_URL",
    "REWARD_URL",
    "TAKUMI_URL",
    "TEAPOT_URL",
    "VERIFY_EMAIL_URL",
    "VERIFY_MMT_URL",
    "WEBAPI_URL",
    "WEBSTATIC_URL",
    "WEB_LOGIN_URL",
    "YSULOG_URL",
    "Route",
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

        if not self.urls[region].get(game):
            raise RuntimeError(f"URL does not support {game.name} game for {region.name} region.")

        return self.urls[region][game]


WEBSTATIC_URL = InternationalRoute(
    "https://operation-webstatic.hoyoverse.com/",
    "https://operation-webstatic.mihoyo.com/",
)

WEBAPI_URL = InternationalRoute(
    "https://webapi-os.account.hoyoverse.com/Api/",
    "https://webapi.account.mihoyo.com/Api/",
)
ACCOUNT_URL = InternationalRoute(
    "https://api-account-os.hoyolab.com/account/auth/api",
    "https://api-takumi.mihoyo.com/account/auth/api/",
)

BBS_URL = InternationalRoute(
    overseas="https://bbs-api-os.hoyolab.com/",
    chinese="https://bbs-api.mihoyo.com/",
)
BBS_REFERER_URL = InternationalRoute(
    overseas="https://www.hoyolab.com/",
    chinese="https://bbs.mihoyo.com/",
)

TAKUMI_URL = InternationalRoute(
    overseas="https://api-os-takumi.mihoyo.com/",
    chinese="https://api-takumi.mihoyo.com/",
)
COMMUNITY_URL = InternationalRoute(
    overseas="https://bbs-api-os.hoyolab.com/community/",
    chinese="https://api-takumi-record.mihoyo.com/community/",
)
RECORD_URL = GameRoute(
    overseas=dict(
        genshin="https://sg-public-api.hoyolab.com/event/game_record/genshin/api",
        hkrpg="https://bbs-api-os.hoyolab.com/game_record/hkrpg/api",
        honkai3rd="https://bbs-api-os.hoyolab.com/game_record/honkai3rd/api",
        nap="https://sg-act-nap-api.hoyolab.com/event/game_record_zzz/api/zzz",
    ),
    chinese=dict(
        genshin="https://api-takumi-record.mihoyo.com/game_record/app/genshin/api",
        hkrpg="https://api-takumi-record.mihoyo.com/game_record/app/hkrpg/api",
        honkai3rd="https://api-takumi-record.mihoyo.com/game_record/app/honkai3rd/api",
        nap="https://api-takumi-record.mihoyo.com/event/game_record_zzz/api/zzz",
    ),
)
NAP_LEDGER_URL = Route("https://sg-public-api.hoyolab.com/event/nap_ledger")

CARD_WAPI_URL = InternationalRoute(
    overseas="https://bbs-api-os.hoyolab.com/game_record/card/wapi",
    chinese="https://api-takumi-record.mihoyo.com/game_record/app/card/wapi",
)
LINEUP_URL = InternationalRoute(
    overseas="https://sg-public-api.hoyoverse.com/event/simulatoros/",
    chinese="https://api-takumi.mihoyo.com/event/platsimulator/",
)

INFO_LEDGER_URL = GameRoute(
    overseas=dict(
        genshin="https://sg-hk4e-api.hoyolab.com/event/ysledgeros/month_info",
        hkrpg="https://sg-public-api.hoyolab.com/event/srledger/month_info",
    ),
    chinese=dict(
        genshin="https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo",
        hkrpg="https://api-takumi.mihoyo.com/event/srledger/month_info",
    ),
)
DETAIL_LEDGER_URL = GameRoute(
    overseas=dict(
        genshin="https://sg-hk4e-api.hoyolab.com/event/ysledgeros/month_detail",
        hkrpg="https://sg-public-api.hoyolab.com/event/srledger/month_detail",
    ),
    chinese=dict(
        genshin="https://hk4e-api.mihoyo.com/event/ys_ledger/monthDetail",
        hkrpg="https://api-takumi.mihoyo.com/event/srledger/month_detail",
    ),
)

CALCULATOR_URL = InternationalRoute(
    overseas="https://sg-public-api.hoyoverse.com/event/calculateos/",
    chinese="https://api-takumi.mihoyo.com/event/e20200928calculate/v1/",
)
CALCULATOR_REFERER_URL = Route("https://webstatic.mihoyo.com/ys/event/e20200923adopt_calculator/index.html")

TEAPOT_URL = InternationalRoute(
    overseas="https://sg-hk4e-api.hoyolab.com/event/e20221121ugcos/",
    chinese="",
)

WIKI_URL = Route("https://sg-wiki-api.hoyolab.com/hoyowiki/wapi")

HK4E_URL = Route("https://sg-hk4e-api.hoyoverse.com/common/hk4e_global/")
NAP_URL = Route("https://sg-announcement-static.hoyoverse.com/common/nap_global/")
HKRPG_URL = Route("https://sg-hkrpg-api.hoyoverse.com/common/hkrpg_global/")

REWARD_URL = GameRoute(
    overseas=dict(
        genshin="https://sg-hk4e-api.hoyolab.com/event/sol?act_id=e202102251931481",
        honkai3rd="https://sg-public-api.hoyolab.com/event/mani?act_id=e202110291205111",
        hkrpg="https://sg-public-api.hoyolab.com/event/luna/os?act_id=e202303301540311",
        nap="https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os?act_id=e202406031448091",
        tot="https://sg-public-api.hoyolab.com/event/luna/os?act_id=e202202281857121",
    ),
    chinese=dict(
        genshin="https://api-takumi.mihoyo.com/event/luna/?act_id=e202311201442471",
        honkai3rd="https://api-takumi.mihoyo.com/event/luna/?act_id=e202306201626331",
        hkrpg="https://api-takumi.mihoyo.com/event/luna/?act_id=e202304121516551",
        nap="https://api-takumi.mihoyo.com/event/luna/zzz?act_id=e202406242138391",
        tot="https://api-takumi.mihoyo.com/event/luna?act_id=e202202251749321",
    ),
)

CODE_URL = GameRoute(
    overseas=dict(
        genshin="https://sg-hk4e-api.hoyoverse.com/common/apicdkey/api/webExchangeCdkey",
        hkrpg="https://sg-hkrpg-api.hoyoverse.com/common/apicdkey/api/webExchangeCdkeyRisk",
        nap="https://public-operation-nap.hoyoverse.com/common/apicdkey/api/webExchangeCdkey",
        tot="https://sg-public-api.hoyoverse.com/common/apicdkey/api/webExchangeCdkey",
    ),
    chinese=dict(),
)

GACHA_URL = GameRoute(
    overseas=dict(
        genshin="https://public-operation-hk4e-sg.hoyoverse.com/gacha_info/api/",
        hkrpg="https://public-operation-hkrpg-sg.hoyoverse.com/common/gacha_record/api/",
        nap="https://public-operation-nap-sg.hoyoverse.com/common/gacha_record/api/",
    ),
    chinese=dict(
        genshin="https://public-operation-hk4e.mihoyo.com/gacha_info/api/",
        hkrpg="https://public-operation-hkrpg.mihoyo.com/common/gacha_record/api/",
        nap="https://public-operation-nap.mihoyo.com/common/gacha_record/api/",
    ),
)
YSULOG_URL = InternationalRoute(
    overseas="https://hk4e-api-os.hoyoverse.com/common/hk4e_self_help_query/User/",
    chinese="https://hk4e-api.mihoyo.com/common/hk4e_self_help_query/User/",
)


COOKIE_V2_REFRESH_URL = Route("https://sg-public-api.hoyoverse.com/account/ma-passport/token/getBySToken")
GET_COOKIE_TOKEN_BY_GAME_TOKEN_URL = Route("https://api-takumi.mihoyo.com/auth/api/getCookieAccountInfoByGameToken")
GET_STOKEN_BY_GAME_TOKEN_URL = Route("https://passport-api.mihoyo.com/account/ma-cn-session/app/getTokenByGameToken")
CN_GET_COOKIE_TOKEN_BY_STOKEN_URL = Route(
    "https://passport-api.mihoyo.com/account/auth/api/getCookieAccountInfoBySToken"
)

WEB_LOGIN_URL = Route("https://sg-public-api.hoyolab.com/account/ma-passport/api/webLoginByPassword")
APP_LOGIN_URL = Route("https://sg-public-api.hoyoverse.com/account/ma-passport/api/appLoginByPassword")
CN_WEB_LOGIN_URL = Route("https://passport-api.miyoushe.com/account/ma-cn-passport/web/loginByPassword")

SEND_VERIFICATION_CODE_URL = Route(
    "https://sg-public-api.hoyoverse.com/account/ma-verifier/api/createEmailCaptchaByActionTicket"
)
VERIFY_EMAIL_URL = Route("https://sg-public-api.hoyoverse.com/account/ma-verifier/api/verifyActionTicketPartly")

CHECK_MOBILE_VALIDITY_URL = Route("https://webapi.account.mihoyo.com/Api/is_mobile_registrable")
MOBILE_OTP_URL = Route("https://passport-api.miyoushe.com/account/ma-cn-verifier/verifier/createLoginCaptcha")
MOBILE_LOGIN_URL = Route("https://passport-api.miyoushe.com/account/ma-cn-passport/web/loginByMobileCaptcha")

CREATE_QRCODE_URL = Route("https://passport-api.miyoushe.com/account/ma-cn-passport/web/createQRLogin")
CHECK_QRCODE_URL = Route("https://passport-api.miyoushe.com/account/ma-cn-passport/web/queryQRLoginStatus")

CREATE_MMT_URL = InternationalRoute(
    overseas="https://sg-public-api.hoyolab.com/event/toolcomsrv/risk/createGeetest?is_high=true",
    chinese="https://api-takumi-record.mihoyo.com/game_record/app/card/wapi/createVerification?is_high=false",
)

VERIFY_MMT_URL = Route("https://sg-public-api.hoyolab.com/event/toolcomsrv/risk/verifyGeetest")

GAME_RISKY_CHECK_URL = InternationalRoute(
    overseas="https://api-account-os.hoyoverse.com/account/risky/api/check",
    chinese="https://gameapi-account.mihoyo.com/account/risky/api/check",
)

SHIELD_LOGIN_URL = GameRoute(
    overseas=dict(
        genshin="https://hk4e-sdk-os.hoyoverse.com/hk4e_global/mdk/shield/api/login",
        honkai3rd="https://bh3-sdk-os.hoyoverse.com/bh3_os/mdk/shield/api/login",
        hkrpg="https://hkrpg-sdk-os.hoyoverse.com/hkrpg_global/mdk/shield/api/login",
        nap="https://nap-sdk-os.hoyoverse.com/nap_global/mdk/shield/api/login",
    ),
    chinese=dict(
        genshin="https://hk4e-sdk.mihoyo.com/hk4e_cn/mdk/shield/api/login",
        honkai3rd="https://api-sdk.mihoyo.com/bh3_cn/mdk/shield/api/login",
        hkrpg="https://hkrpg-sdk.mihoyo.com/hkrpg_cn/mdk/shield/api/login",
        nap="https://nap-sdk.mihoyo.com/nap_cn/mdk/shield/api/login",
    ),
)

PRE_GRANT_TICKET_URL = InternationalRoute(
    overseas="https://api-account-os.hoyoverse.com/account/device/api/preGrantByTicket",
    chinese="https://gameapi-account.mihoyo.com/account/device/api/preGrantByTicket",
)

DEVICE_GRANT_URL = InternationalRoute(
    overseas="https://api-account-os.hoyoverse.com/account/device/api/grant",
    chinese="https://gameapi-account.mihoyo.com/account/device/api/grant",
)

GAME_LOGIN_URL = GameRoute(
    overseas=dict(
        genshin="https://hk4e-sdk-os.hoyoverse.com/hk4e_global/combo/granter/login/v2/login",
        honkai3rd="https://bh3-sdk-os.hoyoverse.com/bh3_os/combo/granter/login/v2/login",
        hkrpg="https://hkrpg-sdk-os.hoyoverse.com/hkrpg_global/combo/granter/login/v2/login",
        nap="https://nap-sdk-os.hoyoverse.com/nap_global/combo/granter/login/v2/login",
    ),
    chinese=dict(
        genshin="https://hk4e-sdk.mihoyo.com/hk4e_cn/combo/granter/login/v2/login",
        honkai3rd="https://api-sdk.mihoyo.com/bh3_cn/combo/granter/login/v2/login",
        hkrpg="https://hkrpg-sdk.mihoyo.com/hkrpg_cn/combo/granter/login/v2/login",
        nap="https://nap-sdk.mihoyo.com/nap_cn/combo/granter/login/v2/login",
    ),
)

GET_USER_REGION_URL = Route(
    "https://api-account-os.hoyoverse.com/account/binding/api/getUserGameRolesOfRegionByCookieToken"
)
GET_FP_URL = InternationalRoute(
    overseas="https://sg-public-data-api.hoyoverse.com/device-fp/api/getFp",
    chinese="https://public-data-api.mihoyo.com/device-fp/api/getFp",
)

MIMO_URL = Route("https://sg-public-api.hoyolab.com/event/e2023mimotravel")

HSR_LINEUP_SIMULATOR_URL = Route("https://sg-public-api.hoyolab.com/event/rpgsimulator")
