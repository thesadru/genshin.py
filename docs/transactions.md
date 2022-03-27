# Transactions

Contains logs of changes to primogems, crystals, resin, artifacts and weapons.

To request any of the wish history endpoints you must set an authkey. Refer to [the authentication section](authentication.md) for more information.

Transaction kinds:

| kind     |       item       | description                                                |
| -------- | :--------------: | ---------------------------------------------------------- |
| primogem | :material-close: | Primogem rewards from daily commissions and events         |
| crystal  | :material-close: | Crystals gotten from top-up purchases                      |
| resin    | :material-close: | Resin lost by claiming boss/domain/leyline rewards         |
| artifact | :material-check: | Artifacts gained from domains or used as level up material |
| weapon   | :material-check: | Weapons gained from wishes or used as level up material    |

> This enum is contained in `genshin.models.TransactionKind`

# Quick example

```py
# iterate over the logs for primogems
async for trans in client.transaction_log("primogem"):
    print(trans)

# set a limit for the iteration
async for trans in client.transaction_log("primogem", limit=100):
    print(trans)

# get and flatten the logs for resin
log = await client.transaction_log("resin", limit=100).flatten()
print(log[-1].time)

# get the first log for artifacts
trans = await client.transaction_log("artifact").first()
print(trans.name)
```

```py
# get multiple transaction kinds combined together
async for trans in client.transaction_log(["artifact", "weapon"]):
    print(trans)

# get all transaction kinds combined together
async for trans in client.transaction_log(limit=20):
    print(trans)
```
