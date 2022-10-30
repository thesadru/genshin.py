# CLI

Genshin.py is not only a library but also a <abbr title="Command Line Interface">CLI</abbr> app.

Authentication is required for most commands. Cookies can be provided either through `--cookies "ltoken=...; ltuid=..."` or gotten implicitly from the browser.

## Installation

```console
pip install genshin[cli]
```

## Usage

### Get help

```console
$ python -m genshin --help
Usage: python -m genshin [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  accounts    Get all of your genshin accounts.
  banner-ids  Get the banner ids from logs.
  genshin     Genshin-related commands.
  honkai      Honkai-related commands.
  lineups     Show popular genshin lineups.
  login       Login with a password.
  pity        Calculate the amount of pulls until pity.
  wishes      Show a nicely formatted wish history.
```

### Run a command

```console
$ python -m genshin genshin stats 710785423
User stats of 710785423

Stats:
Achievements: 436
Days Active: 464
Characters: 33
Waypoints Unlocked: 169
Domains Unlocked: 33
Anemoculi: 66
Geoculi: 131
Electroculi: 180
Common Chests Opened: 1162
Exquisite Chests Opened: 924
Precious Chests Opened: 262
Luxurious Chests Opened: 106
Remarkable Chests Opened: 42

Explorations:
Enkanomiya: explored 67.9% | Offering level 0
Inazuma: explored 98.1% | Reputation level 10
Dragonspine: explored 96.1% | Offering level 12
Liyue: explored 93.5% | Reputation level 8
Mondstadt: explored 100.0% | Reputation level 8

Teapot:
level 10 | comfort 21220 (Fit for a King)
Unlocked realms: Floating Abode, Emerald Peak, Cool Isle
```
