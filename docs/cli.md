# CLI

Genshin.py is not only a library but also a <abbr title="Command Line Interface">CLI</abbr> app.

For it to work you must be logged into your genshin account on any of your browsers. (Refer to [the authentication section](authentication.md#setting-cookies-automatically) for reasoning)

## Installation

```console
pip install genshin[cli]
```

## Usage

### Get help

```console
$ genshin --help
Usage: genshin [OPTIONS] COMMAND [ARGS]...

Options:
  --help                Show this message and exit.

Commands:
  accounts    Get all of your genshin accounts
  characters  Show the characters of a user
  notes       Real-Time notes to see live genshin data
  pity        Calculates the amount of pulls until pity
  stats       Show simple statistics of a user
  wishes      Get a nicely formatted wish history
```

### Run a command

```console
$ genshin stats 710785423
User stats of 710785423

Stats:
Achievements: 387
Days Active: 321
Characters: 28
Spiral Abyss: 11-3
Anemoculi: 66
Geoculi: 131
Electroculi: 180
Common Chests: 1076
Exquisite Chests: 880
Precious Chests: 246
Luxurious Chests: 103
Remarkable Chests: 42
Unlocked Waypoints: 136
Unlocked Domains: 31

Explorations
Inazuma: explored 97.5% | Reputation level 10
Dragonspine: explored 95.3% | Offering level 12
Liyue: explored 93.0% | Reputation level 8
Mondstadt: explored 100.0% | Reputation level 8

Teapot
level 9 | comfort 20920 (Fit for a King)
Unlocked realms: Emerald Peak, Cool Isle
```
