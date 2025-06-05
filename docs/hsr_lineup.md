# HSR Lineup Simulator

This is a HoYoLAB feature that allows players to submit the teams and buffs they used for the endgame challenges (MOC, Pure Fiction, and Apocalyptic Shadow.)

## Example

The following code example shows all the possible API features the wrapper can currently utilize.

```py
import genshin

client = genshin.Client(lang="en-us") # (1)
client = genshin.Client(cookies, uid=809162009, lang="zh-cn") # (2)

game_modes = await client.get_starrail_lineup_game_modes()
for mode in game_modes:
    print(f"{mode.name} ({mode.type})")
    for floor in mode.floors:
        print(floor.name)

moc_stage11 = client.get_starrail_lineup_floor(game_modes, type="Chasm", floor=11) # (3)
moc_stage11 = client.get_starrail_lineup_floor(game_modes, type=genshin.models.StarRailGameModeType.MOC, floor=11) # (4)

if moc_stage11 is None:
    print("MOC Stage 11 not found.")
    return
print(moc_stage11)

schedules = await client.get_starrail_lineup_schedules("Chasm") # (5)
for schedule in schedules:
    print(f"{schedule.id} - {schedule.name} ({schedule.start_time} ~ {schedule.end_time})")

# Get lineups for the current season for MOC Stage 11
schedule = schedules[0]
next_page_token = None
for _ in range(5):
    page = await client.get_starrail_lineups( # (6)
        tag_id=moc_stage11.id,
        group_id=schedule.id,
        type="Chasm",
        next_page_token=next_page_token,
    )
    for lineup in page.lineups:
        print(lineup.title)
    next_page_token = page.next_page_token
```

1. The `lang` parameter matters for the language of lineups returned by the API.
2. `cookies` and `uid` parameters are optional; if passed in, using the `Match` order in `get_starrail_lineups` will return lineups with characters that the user has.
3. Use the helper method to get stage 11 of MOC.
4. You can also use the enum for the game mode type.
5. Get the MOC schedules (sort by most recent first.)
6. 10 lineups are fetched per request, use the `next_page_token` to get the next page of results.
