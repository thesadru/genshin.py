
import hashlib
import random
import string
import time
from .constants import CHARACTER_NAMES

def generate_ds_token(salt: str) -> str:
    """Creates a new ds token for authentication."""
    t = int(time.time())
    r = "".join(random.choices(string.ascii_letters, k=6))
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()
    return f"{t},{r},{h}"


def recognize_server(uid: int) -> str:
    """Recognizes which server a UID is from."""
    server = {
        "1": "cn_gf01",
        "5": "cn_qd01",
        "6": "os_usa",
        "7": "os_euro",
        "8": "os_asia",
        "9": "os_cht",
    }.get(str(uid)[0])

    if server:
        return server
    else:
        raise Exception(f"UID {uid} isn't associated with any server")

