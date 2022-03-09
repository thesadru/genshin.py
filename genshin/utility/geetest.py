"""Geetest utilities."""
import base64
import time
import typing

import aiohttp

__all__ = ["create_mmt", "encrypt_geetest_password"]


LOGIN_KEY_CERT = b"""
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDvekdPMHN3AYhm/vktJT+YJr7
cI5DcsNKqdsx5DZX0gDuWFuIjzdwButrIYPNmRJ1G8ybDIF7oDW2eEpm5sMbL9zs
9ExXCdvqrn51qELbqj0XxtMTIpaCHFSI50PfPpTFV9Xt/hmyVwokoOXFlAEgCn+Q
CgGs52bFoYMtyi+xEQIDAQAB
-----END PUBLIC KEY-----
"""


async def create_mmt(now: typing.Optional[int] = None) -> typing.Mapping[str, typing.Any]:
    """Create a new hoyolab mmt."""
    async with aiohttp.ClientSession() as session:
        r = await session.get(
            "https://webapi-os.account.hoyolab.com/Api/create_mmt",
            params=dict(scene_type=1, now=now or int(time.time()), region="os"),
        )

        data = await r.json()

    return data["data"]["mmt_data"]


def encrypt_geetest_password(text: str) -> str:
    """Encrypt text for geetest."""
    import rsa

    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(LOGIN_KEY_CERT)
    crypto = rsa.encrypt(text.encode("utf-8"), public_key)
    return base64.b64encode(crypto).decode("utf-8")
