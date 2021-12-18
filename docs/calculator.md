# Enhancment Progress Calculator

A wrapper around the [Genshin Impact Enhancment Progress Calculator](https://webstatic-sea.mihoyo.com/ys/event/calculator-sea/index.html) page.
Contains a database of all characters, weapons and artifacts. Also the only way to recieve talents.

To request any of the calculator endpoints you must first be logged in. Refer to [the authentication section](authentication.md) for more information.

## Quick Example

```py
# get a list of all characters
characters = await client.get_calculator_characters()

# get a list of all weapons
weapons = await client.get_calculator_weapons()

# get a list of all artifacts
artifacts = await client.get_calculator_artifacts()

# search for a specific character/weapon/artifact
characters = await client.get_calculator_characters(query="Xi")

# filter the returned characters/weapons/artifacts
weapons = await client.get_calculator_weapons(rarities=[5, 4])

# get all talents of a character
talents = await client.get_character_talents(10000002)

# get all other artifacts in a set
artifacts = await client.get_complete_artifact_set(7554)
```

```py
# get a list of synced characters
# only returns the characters you have and ensures all level fields are provided
characters = await client.get_calculator_characters(sync=True)

# get the details of a character
# includes their weapon, artifacts and talents
details = await client.get_character_details(10000002)
```

## Example Of Calculation

```py
# calculate the amount of resources needed for any character

# id of Ayaka
character_id = 10000002
# a calulator object: calculate resources needed to level up ayaka from level 1 to 90
obj = genshin.models.CalculatorObject(id=character_id, current=1, target=90)
cost = await client.calculate(character=obj)

# if you know what you're doing you may simply pass in a tuple
# this is possible because is just a named tuple CalculatorObject
# remember that CalculatorObject is optional literally everywhere
cost = await client.calculate(character=(character_id, 1, 90))
```

```py
# calculate the amount of resources needed for a weapon
# here we want to level up Staff of Homa from level 20 to level 70
cost = await client.calculate(weapon=(13501, 20, 70))
```

```py
# calculate the amount of resources needed for an artifact

# here we us the 5* gladiator's nostalgia
artifact_id = 7554
# we probably want all artifacts so we may use get_complete_artifact_set to get all others
artifacts = await client.get_complete_artifact_set(artifact_id)

# to calculate we can pass in a list or a dict
# both of these are valid:
cost = await client.calculate(
    artifacts=[
        (artifact_id, 0, 20),
        (artifact[0].id, 0, 20),
        (artifact[1].id, 0, 20),
        (artifact[2].id, 0, 20),
        (artifact[3].id, 0, 20),
    ]
)
cost = await client.calculate(
    artifacts={
        artifact_id: (0, 20),
        artifact[0].id: (0, 20),
        artifact[1].id: (0, 20),
        artifact[2].id: (0, 20),
        artifact[3].id: (0, 20),
    }
)
```

```py
# calculate the amount of resources needed for a talent artifact
talents = await client.get_character_talents(character_id)

# we have to make sure that we only request upgradeable talents
talents = [talent for talent in talents if talent.upgradeable]

# talents, unlike other fields, require to be passed by their group_id
cost = await client.calculate(
    talents={
        talents[0].group_id: (1, 10),
        talents[1].group_id: (1, 10),
        talents[2].group_id: (1, 10)
    }
)
```

```py
# finally we can combine them all together
character_id = 10000002
weapon_id = 13501
artifact_id = 7554

artifacts = await client.get_complete_artifact_set(artifact_id)
artifact_ids = [artifact_id] + [a.id for a in artifacts]

talents = await client.get_character_talents(character_id)
talent_ids = [talent.group_id for talent in talents if talent.upgradeable]

cost = await client.calculate(
    character=(character_id, 0, 90),
    weapon=(weapon_id, 0, 90),
    artifacts={a: (0, 20) for a in artifact_ids},
    talents={t: (0, 10) for t in talent_ids},
)

# let's see how much everything costs:
print(cost.character)
print(cost.weapon)
print(cost.artifacts)
print(cost.talents)

# and see the total cost
print(cost.total)
```

```py
# alternatively, we can just try and upgrade everything our character has equipped
characters = await client.get_calculator_characters(sync=True)
character = characters[0]
details = await client.get_character_details(character.id)

cost = await client.calculate(
    character=(character.id, character.level, character.max_level),
    weapon=(details.weapon.id, details.weapon.level, details.weapon.max_level),
    artifacts={a.id: (a.level, a.max_level) for a in details.artifacts},
    talents={t.group_id: (t.level, t.max_level) for t in details.talents},
)

for item in cost.total:
    print(f"{item.amount}x {item.name}")
```
