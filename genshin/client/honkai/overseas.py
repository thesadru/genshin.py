
# import genshin.client.honkai.base as honkai_base
from genshin.client.honkai.base import BaseHonkaiClient
from genshin.client import adapter, base

class BaseOverseasHonkaiClient(BaseHonkaiClient):
    DS_SALT = "6cqshh5dhw73bzxn20oexa9k516chk7s"
    ACT_ID = "e202110291205111"

    TAKUMI_URL = "https://api-os-takumi.mihoyo.com/"
    RECORD_URL = "https://bbs-api-os.mihoyo.com/game_record/"
    REWARD_URL = "https://api-os-takumi.mihoyo.com/event/mani/"

class OverseasHonkaiClient(BaseOverseasHonkaiClient, adapter.Adapter):
    """Standard implementation of an overseas genshin client"""