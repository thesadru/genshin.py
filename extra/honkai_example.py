import asyncio
from typing import List

import genshin

from genshin.models import HonkaiFullUserStats, SuperstringAbyss


# NOTE: First and foremost, these are all temporary. All of this uncomfortable stuff will soon:tm:
# be replaced with the comfort of a HonkaiClient. Also, note that these examples won't work unless
# you provide them with actual cookies. Until we have a HonkaiClient, we will take advanrage of
# GenshinClient.request_game_record(). The API data can be parsed as follows:

cookies = {"ltuid": "17334943", "ltoken": "uEecA6eaelVrOoPwiVmLf880jeQlXB7srhtniGi1"}


async def get_abyss_data(uid) -> List[SuperstringAbyss]:
    client = genshin.GenshinClient(cookies)
    response = await client.request_game_record(
        "honkai3rd/api/newAbyssReport", params={"server": "eur01", "role_id": uid}
    )
    return [SuperstringAbyss(**report) for report in response["reports"]]


abyss_data = asyncio.run(get_abyss_data(200365120))

latest_abyss_run = abyss_data[0]
lead_valkyrie = latest_abyss_run.lineup[0]
print(lead_valkyrie.icon)


# To get all data shown on https://webstatic-sea.mihoyo.com/app/community-game-records-sea/index.html#/bh3,
# (== what GenshinClient.get_full_user(<uid>) would return for the genshin page) the following snippet is of use.
# This (+/- some changes) will one day all be under the hood of HonkaiClient.get_full_user(<uid>).


async def get_full_user(uid: int) -> HonkaiFullUserStats:
    client = genshin.GenshinClient(cookies)
    params = {"server": "eur01", "role_id": uid}
    user_data = await client.request_game_record("honkai3rd/api/index", lang="en-us", params=params)
    abyss_data = await client.request_game_record("honkai3rd/api/newAbyssReport", params=params)
    ER_data = await client.request_game_record("honkai3rd/api/godWar", params=params)
    char_data = await client.request_game_record("honkai3rd/api/characters", params=params)
    MA_data = await client.request_game_record("honkai3rd/api/battleFieldReport", params=params)

    return HonkaiFullUserStats(
        **user_data,
        battlesuits=[char["character"] for char in char_data["characters"]],
        abyss=abyss_data["reports"],
        memorial_arena=MA_data["reports"],
        elysian_realm=ER_data["records"]
    )


user_data = asyncio.run(get_full_user(200365120))

print(user_data.stats.battlesuits_SSS)
print(user_data.battlesuits[0].icon)
print(user_data.abyss[0].lineup[0].icon)  # should print the same as the first print
