"""Geetest utilities."""
import base64
import typing
import json

__all__ = ["encrypt_geetest_credentials"]


# RSA key is the same for app and web login
LOGIN_KEY_CERT = b"""
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

WEB_LOGIN_HEADERS = {
    "x-rpc-app_id": "c9oqaq3s3gu8",
    "x-rpc-client_type": "4",
    "x-rpc-sdk_version": "2.14.1",
    "x-rpc-game_biz": "bbs_oversea",
    "x-rpc-source": "v2.webLogin",
    "x-rpc-referrer": "https://www.hoyolab.com",
    # If not equal account.hoyolab.com It's will return retcode 1200 [Unauthorized]
    "Origin": "https://account.hoyolab.com",
    "Referer": "https://account.hoyolab.com/",
}

APP_LOGIN_HEADERS = {
    "x-rpc-app_id": "c9oqaq3s3gu8",
    "x-rpc-app_version": "2.47.0",
    "x-rpc-client_type": "2",
    "x-rpc-sdk_version": "2.22.0",
    "x-rpc-game_biz": "bbs_oversea",
    "Origin": "https://account.hoyoverse.com",
    "Referer": "https://account.hoyoverse.com/",
}

EMAIL_SEND_HEADERS = {
    "x-rpc-app_id": "c9oqaq3s3gu8",
}

EMAIL_VERIFY_HEADERS = {
    "x-rpc-app_id": "c9oqaq3s3gu8",
}


def encrypt_geetest_credentials(text: str) -> str:
    """Encrypt text for geetest."""
    import rsa

    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(LOGIN_KEY_CERT)
    crypto = rsa.encrypt(text.encode("utf-8"), public_key)
    return base64.b64encode(crypto).decode("utf-8")

def get_aigis_header(session_id: str, mmt_data: typing.Dict[str, typing.Any]) -> str:
    """Get aigis header."""
    return f"{session_id};{base64.b64encode(json.dumps(mmt_data).encode()).decode()}"