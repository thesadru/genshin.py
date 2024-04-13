"""Auth utilities."""

import base64
import hmac
import json
import typing

from hashlib import sha256
from genshin import constants

__all__ = ["encrypt_geetest_credentials", "generate_sign"]


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
    "Origin": "https://user.miyoushe.com",
    "Referer": "https://user.miyoushe.com/",
    "x-rpc-source": "v2.webLogin",
    "x-rpc-mi_referrer": "https://user.miyoushe.com/login-platform/index.html?app_id=bll8iq97cem8&theme=&token_type=4&game_biz=bbs_cn&message_origin=https%253A%252F%252Fwww.miyoushe.com&succ_back_type=message%253Alogin-platform%253Alogin-success&fail_back_type=message%253Alogin-platform%253Alogin-fail&ux_mode=popup&iframe_level=1#/login/password",  # noqa: E501
    "x-rpc-device_id": "586f2440-856a-4243-8076-2b0a12314197",
}

EMAIL_SEND_HEADERS = {
    "x-rpc-app_id": "c9oqaq3s3gu8",
    "x-rpc-client_type": "2",
}

EMAIL_VERIFY_HEADERS = {
    "x-rpc-app_id": "c9oqaq3s3gu8",
    "x-rpc-client_type": "2",
}

CREATE_MMT_HEADERS = {
    "x-rpc-app_version": "2.60.1",
    "x-rpc-client_type": "5",
}

DEVICE_ID = "D6AF5103-D297-4A01-B86A-87F87DS5723E"

RISKY_CHECK_HEADERS = {
    "x-rpc-client_type": "1",
    "x-rpc-channel_id": "1",
    "x-rpc-game_biz": "hkrpg_global",
}

SHIELD_LOGIN_HEADERS = {
    "x-rpc-client_type": "1",
    "x-rpc-channel_id": "1",
    "x-rpc-game_biz": "hkrpg_global",
    "x-rpc-device_id": DEVICE_ID,
}

GRANT_TICKET_HEADERS = {
    "x-rpc-client_type": "1",
    "x-rpc-channel_id": "1",
    "x-rpc-game_biz": "hkrpg_global",
    "x-rpc-device_id": DEVICE_ID,
    "x-rpc-language": "ru",
}

GAME_LOGIN_HEADERS = {
    "x-rpc-client_type": "1",
    "x-rpc-channel_id": "1",
    "x-rpc-game_biz": "hkrpg_global",
    "x-rpc-device_id": DEVICE_ID,
}

GEETEST_LANGS = {
    "简体中文": "zh-cn",
    "繁體中文": "zh-tw",
    "Deutsch": "de",
    "English": "en",
    "Español": "es",
    "Français": "fr",
    "Indonesia": "id",
    "Italiano": "it",
    "日本語": "ja",
    "한국어": "ko",
    "Português": "pt-pt",
    "Pусский": "ru",
    "ภาษาไทย": "th",
    "Tiếng Việt": "vi",
    "Türkçe": "tr",
}


def lang_to_geetest_lang(lang: str) -> str:
    """Convert `client.lang` to geetest lang."""
    return GEETEST_LANGS.get(constants.LANGS.get(lang, "en-us"), "en")


def encrypt_geetest_credentials(text: str, key_type: typing.Literal[1, 2]) -> str:
    """Encrypt text for geetest."""
    import rsa

    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(LOGIN_KEY_TYPE_1 if key_type == 1 else LOGIN_KEY_TYPE_2)
    crypto = rsa.encrypt(text.encode("utf-8"), public_key)
    return base64.b64encode(crypto).decode("utf-8")


def get_aigis_header(session_id: str, mmt_data: typing.Dict[str, typing.Any]) -> str:
    """Get aigis header."""
    return f"{session_id};{base64.b64encode(json.dumps(mmt_data).encode()).decode()}"


def generate_sign(data: typing.Dict[str, typing.Any], key: str) -> str:
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
