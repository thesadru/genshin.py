"""Auth utilities."""

import base64
import hmac
import json
import typing
from hashlib import sha256

from genshin import types

__all__ = ["encrypt_credentials", "generate_sign"]


# RSA key used for OS app/web login
LOGIN_KEY_TYPE_1 = b"""
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4PMS2JVMwBsOIrYWRluY
wEiFZL7Aphtm9z5Eu/anzJ09nB00uhW+ScrDWFECPwpQto/GlOJYCUwVM/raQpAj
/xvcjK5tNVzzK94mhk+j9RiQ+aWHaTXmOgurhxSp3YbwlRDvOgcq5yPiTz0+kSeK
ZJcGeJ95bvJ+hJ/UMP0Zx2qB5PElZmiKvfiNqVUk8A8oxLJdBB5eCpqWV6CUqDKQ
KSQP4sM0mZvQ1Sr4UcACVcYgYnCbTZMWhJTWkrNXqI8TMomekgny3y+d6NX/cFa6
6jozFIF4HCX5aW8bp8C8vq2tFvFbleQ/Q3CU56EWWKMrOcpmFtRmC18s9biZBVR/
8QIDAQAB
-----END PUBLIC KEY-----
"""

# RSA key used for CN app/game and game login
LOGIN_KEY_TYPE_2 = b"""
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDvekdPMHN3AYhm/vktJT+YJr7
cI5DcsNKqdsx5DZX0gDuWFuIjzdwButrIYPNmRJ1G8ybDIF7oDW2eEpm5sMbL9zs
9ExXCdvqrn51qELbqj0XxtMTIpaCHFSI50PfPpTFV9Xt/hmyVwokoOXFlAEgCn+Q
CgGs52bFoYMtyi+xEQIDAQAB
-----END PUBLIC KEY-----
"""

WEB_LOGIN_HEADERS = {
    "x-rpc-app_id": "c9oqaq3s3gu8",
    "x-rpc-client_type": "4",
    # If not equal account.hoyolab.com It's will return retcode 1200 [Unauthorized]
    "Origin": "https://account.hoyolab.com",
    "Referer": "https://account.hoyolab.com/",
}

APP_LOGIN_HEADERS = {
    "x-rpc-app_id": "c9oqaq3s3gu8",
    "x-rpc-client_type": "2",
    # Passing "x-rpc-device_id" header will trigger email verification
    # (unless the device_id is already verified).
    #
    # For some reason, without this header, email verification is not triggered.
    # "x-rpc-device_id": "1c33337bd45c1bfs",
}

CN_LOGIN_HEADERS = {
    "x-rpc-app_id": "bll8iq97cem8",
    "x-rpc-client_type": "4",
    "x-rpc-source": "v2.webLogin",
    "x-rpc-device_fp": "38d7fff8fd68c",
    "x-rpc-device_id": "469af8a4-0754-4a3c-a999-dec592f00894",
    "x-rpc-device_model": "Firefox%20131.0",
    "x-rpc-device_name": "Firefox",
    "x-rpc-game_biz": "bbs_cn",
    "x-rpc-sdk_version": "2.31.0",
}

EMAIL_SEND_HEADERS = {
    "x-rpc-app_id": "c9oqaq3s3gu8",
    "x-rpc-client_type": "2",
}

EMAIL_VERIFY_HEADERS = {
    "x-rpc-app_id": "c9oqaq3s3gu8",
    "x-rpc-client_type": "2",
}

QRCODE_HEADERS = {
    "x-rpc-app_id": "bll8iq97cem8",
    "x-rpc-client_type": "4",
    "x-rpc-game_biz": "bbs_cn",
    "x-rpc-device_fp": "38d7fa104e5d7",
    "x-rpc-device_id": "586f1440-856a-4243-8076-2b0a12314197",
}

CREATE_MMT_HEADERS = {
    types.Region.OVERSEAS: {
        "x-rpc-challenge_path": "https://bbs-api-os.hoyolab.com/game_record/app/hkrpg/api/challenge",
        "x-rpc-app_version": "2.55.0",
        "x-rpc-challenge_game": "6",
        "x-rpc-client_type": "5",
    },
    types.Region.CHINESE: {
        "x-rpc-app_version": "2.60.1",
        "x-rpc-client_type": "5",
        "x-rpc-challenge_game": "6",
        "x-rpc-page": "v1.4.1-rpg_#/rpg",
        "x-rpc-tool-version": "v1.4.1-rpg",
    },
}

DEVICE_ID = "D6AF5103-D297-4A01-B86A-87F87DS5723E"

RISKY_CHECK_HEADERS = {
    "x-rpc-client_type": "1",
    "x-rpc-channel_id": "1",
}

SHIELD_LOGIN_HEADERS = {
    "x-rpc-client_type": "1",
    "x-rpc-channel_id": "1",
    "x-rpc-device_id": DEVICE_ID,
}

GRANT_TICKET_HEADERS = {
    "x-rpc-client_type": "1",
    "x-rpc-channel_id": "1",
    "x-rpc-device_id": DEVICE_ID,
    "x-rpc-language": "en",
}

GAME_LOGIN_HEADERS = {
    "x-rpc-client_type": "1",
    "x-rpc-channel_id": "1",
    "x-rpc-device_id": DEVICE_ID,
}

GEETEST_LANGS: typing.Final[typing.Dict[types.Lang, str]] = {
    "zh-cn": "zh-cn",
    "zh-tw": "zh-tw",
    "de-de": "de",
    "en-us": "en",
    "es-es": "es",
    "fr-fr": "fr",
    "id-id": "id",
    "it-it": "it",
    "ja-jp": "ja",
    "ko-kr": "ko",
    "pt-pt": "pt-pt",
    "ru-ru": "ru",
    "th-th": "th",
    "vi-vn": "vi",
    "tr-tr": "tr",
}


def lang_to_geetest_lang(lang: types.Lang) -> str:
    """Convert `client.lang` to geetest lang."""
    return GEETEST_LANGS.get(lang, "en")


def encrypt_credentials(text: str, key_type: typing.Literal[1, 2]) -> str:
    """Encrypt text for geetest."""
    import rsa

    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(LOGIN_KEY_TYPE_1 if key_type == 1 else LOGIN_KEY_TYPE_2)
    crypto = rsa.encrypt(text.encode("utf-8"), public_key)
    return base64.b64encode(crypto).decode("utf-8")


def get_aigis_header(session_id: str, mmt_data: dict[str, typing.Any]) -> str:
    """Get aigis header."""
    return f"{session_id};{base64.b64encode(json.dumps(mmt_data).encode()).decode()}"


def generate_sign(data: dict[str, typing.Any], key: str) -> str:
    """Generate a sign for the given `data` and `app_key`."""
    string = ""
    for k in sorted(data.keys()):
        string += k + "=" + str(data[k]) + "&"
    return hmac.new(key.encode(), string[:-1].encode(), sha256).hexdigest()


def generate_risky_header(
    check_id: str,
    challenge: str = "",
    validate: str = "",
) -> str:
    """Generate risky header for geetest verification."""
    return f"id={check_id};c={challenge};s={validate}|jordan;v={validate}"
