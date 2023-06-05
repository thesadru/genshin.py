"""Geetest utilities."""
import base64
import json
import typing

import aiohttp

import genshin.errors as error

__all__ = ["create_mmt", "encrypt_geetest_password"]


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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.37",
    "x-rpc-app_id": "c9oqaq3s3gu8",
    "x-rpc-client_type": "4",
    "x-rpc-sdk_version": "2.14.1",
    "x-rpc-game_biz": "bbs_oversea",
    "x-rpc-source": "v2.webLogin",
    "x-rpc-device_model": "Microsoft Edge 114.0.1823.37",
    "x-rpc-device_name": "Microsoft Edge",
    "x-rpc-referrer": "https://www.hoyolab.com",
    # If not equal account.hoyolab.com It's will return retcode 1200 [Unauthorized]
    "Origin": "https://account.hoyolab.com",
    "Referer": "https://account.hoyolab.com/"
}


async def create_mmt(account: str, password: str) -> typing.Mapping[str, typing.Any]:
    """Create a new hoyolab mmt."""
    async with aiohttp.ClientSession() as session:
        _payload = {
            "account": encrypt_geetest_password(account),
            "password": encrypt_geetest_password(password),
            "token_type": 6
        }

        r = await session.post(
            "https://sg-public-api.hoyolab.com/account/ma-passport/api/webLoginByPassword",
            json=_payload,
            headers=HEADERS
        )

        data = await r.json()

        if data["retcode"] == -3101:
            session = json.loads(r.headers["x-rpc-aigis"])

            return {
                **session,
                "data": json.loads(session["data"])
            }
        
        error.raise_for_retcode(data)


def encrypt_geetest_password(text: str) -> str:
    """Encrypt text for geetest."""
    import rsa

    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(LOGIN_KEY_CERT)
    crypto = rsa.encrypt(text.encode("utf-8"), public_key)
    return base64.b64encode(crypto).decode("utf-8")
