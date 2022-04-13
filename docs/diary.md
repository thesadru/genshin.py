# Traveler's Diary

Contains statistics of earned primogems and mora in the last 3 months.

To request any of the diary endpoints you must first be logged in. Refer to [the authentication section](authentication.md) for more information.

# Quick Example

```py
# get the diary
diary = await client.get_diary()

print(f"Primogems earned this month: {diary.data.current_primogems}")
for category in diary.data.categories:
    print(f"{category.percentage}% earned from {category.name} ({category.amount} primogems)")
```

```py
# get the log of actions which earned primogems
async for action in client.diary_log(limit=50):
    print(f"{action.action} - {action.amount} primogems")

# get the diary log for mora
async for action in client.diary_log(limit=50, type=genshin.models.DiaryType.MORA):
    print(f"{action.action} - {action.amount} mora")
```
