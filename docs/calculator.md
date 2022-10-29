# Enhancment Progress Calculator

A wrapper around the [Genshin Impact Enhancment Progress Calculator](https://webstatic-sea.mihoyo.com/ys/event/calculator-sea/index.html) page.
Contains a database of all characters, weapons and artifacts. Also the only way to recieve talents.

To request many of the calculator endpoints you must first be logged in. Refer to [the authentication section](authentication.md) for more information.

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

### Basic Calculation

The calculator uses builders to set data. All methods return `self` so they're chainable.

```py
# create a builder object
builder = client.calculator()
# calculate resoources needed to level up Hu Tao from lvl 1 to lvl 90
builder.set_character(10000046, current=1, target=90)
# calculate the amount of resources needed for a Staff of Homa from level 20 to level 70
builder.set_weapon(13501, current=20, target=70)

# execute the builder
cost = await builder.calculate()
print(cost)
```

```py
# you may also chain the builder (recommended)
cost = await (
    client.calculator()
    .set_character(10000046, current=1, target=90)
    .set_weapon(13501, current=20, target=70)
)

```

```py
# calculate the amount needed for a 5* gladiator's nostalgia
artifact_id = 7554
cost = await (
    client.calculator()
    .add_artifact(artifact_id, current=0, target=20)
)

# or calculate for a full set
cost = await (
    client.calculator()
    .set_artifact_set(artifact_id, current=0, target=20)
)
```

### Calculation based off a character

If we assume we're calculating resources for the currently logged in user we can simply get their weapon and artifact levels directly.

```py
# Let's use the currently equipped weapon, artifacts and talents
cost = await (
    client.calculator()
    .set_character(10000046, current=1, target=90)
    .with_current_weapon(target=70)
    .with_current_artifacts(target=20) # every artifact will be set to lvl 20
    .with_current_talents(target=7) # every artifact will be set to lvl 7
)
```

```py
# you may want to upgrade only specific talent or artifact types
cost = await (
    client.calculator()
    .set_character(10000046, current=80, target=90)
    # upgrade only the flower and feather
    .with_current_artifacts(flower=16, feather=20)
    # upgrade only the burst
    .with_current_talents(burst=10)
)
```
