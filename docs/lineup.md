# Lineup

Contains recommended character builds and teams for world exploration and domains.

To request many of the Battle Chronicle endpoints you must first be logged in. Refer to [the authentication section](authentication.md) for more information.

# Quick Example

```py
# get scenarios
scenarios = await client.get_lineup_scenarios()

# get lineups
lineups = await client.get_lineups(scenarios.abyss.spire, limit=20)

# get lineup details
lineup = await client.get_lineup_details(lineups[0].id)

# get further field info of lineups
lineup = await client.get_lineup_fields()
```

Some scenario ids:

| name               | id  |
| ------------------ | --- |
| World Exploration  | 1   |
| Trounce Domains    | 3   |
| Domain Challenges  | 9   |
| Boss Battles       | 24  |
| Spiral Abyss       | 2   |
| Abyssal Moon Spire | 41  |

> Partial data of `get_lineup_fields`
