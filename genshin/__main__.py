import asyncio
from functools import update_wrapper
from typing import Any, Awaitable, Callable

import typer

import genshin

app = typer.Typer(name="genshin")


def asynchronous(func: Callable[..., Awaitable[Any]]) -> Callable[..., Any]:
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return update_wrapper(wrapper, func)


@app.command()
@asynchronous
async def stats(
    uid: int = typer.Argument(..., help="A genshin uid"),
    lang: str = typer.Option("en-us", help="The language to use"),
):
    """Show simple statistics of a user"""
    cuid = typer.style(str(uid), fg="blue")
    typer.echo(f"User stats of {cuid}\n")

    async with genshin.GenshinClient() as client:
        client.set_browser_cookies()
        data = await client.get_partial_user(uid, lang=lang)

    typer.secho("Stats:", fg="yellow")
    for k, v in data.stats.as_dict().items():
        value = typer.style(str(v), bold=True)
        typer.echo(f"{k}: {value}")

    typer.echo()
    typer.secho("Explorations", fg="yellow")
    for area in data.explorations:
        perc = typer.style(str(area.percentage) + "%", bold=True)
        typer.echo(f"{area.name}: explored {perc} | {area.type} level {area.level}")

    if data.teapot is not None:
        typer.echo()
        typer.secho("Teapot", fg="yellow")
        level = typer.style(str(data.teapot.level), bold=True)
        comfort = typer.style(str(data.teapot.comfort), bold=True)
        typer.echo(f"level {level} | comfort {comfort} ({data.teapot.comfort_name})")
        typer.echo(f"Unlocked realms: {', '.join(r.name for r in data.teapot.realms)}")


@app.command()
@asynchronous
async def characters(
    uid: int = typer.Argument(..., help="A genshin uid"),
    lang: str = typer.Option("en-us", help="The language to use"),
):
    """Show the characters of a user"""
    cuid = typer.style(str(uid), fg="blue")
    typer.echo(f"Characters of {cuid}")

    async with genshin.GenshinClient() as client:
        client.set_browser_cookies()
        data = await client.get_user(uid, lang=lang)

    characters = sorted(data.characters, key=lambda c: (c.level, c.rarity), reverse=True)
    for char in characters:
        color = {
            "Anemo": "bright_green",
            "Pyro": "red",
            "Hydro": "bright_blue",
            "Electro": "magenta",
            "Cryo": "bright_cyan",
            "Geo": "yellow",
            "Dendro": "green",
        }[char.element]

        typer.echo()
        name = typer.style(char.name, bold=True)
        element = typer.style(char.element, fg=color)
        typer.echo(f"{name} ({'★' * char.rarity} {element})")
        typer.echo(f"lvl {char.level} C{char.constellation}, friendship lvl {char.friendship}")
        typer.echo(
            f"Weapon: {char.weapon.name} ({'★' * char.weapon.rarity} {char.weapon.type}) - "
            f"lvl {char.weapon.level} R{char.weapon.refinement}"
        )
        if char.artifacts:
            typer.echo("Artifacts:")
            for arti in char.artifacts:
                typer.echo(f" - {arti.pos_name}: {arti.set.name} ({'★' * arti.rarity})")
        if char.outfits:
            typer.echo(f"Outfits: {', '.join(o.name for o in char.outfits)}")


@app.command()
@asynchronous
async def notes(
    uid: int = typer.Argument(..., help="A genshin uid"),
    lang: str = typer.Option("en-us", help="The language to use"),
):
    cuid = typer.style(str(uid), fg="blue")
    typer.echo(f"Real-Time notes of {cuid}")

    async with genshin.GenshinClient() as client:
        client.set_browser_cookies()
        data = await client.get_notes(uid, lang=lang)

    typer.echo(f"{typer.style('Resin:', bold=True)} {data.current_resin}/{data.max_resin}")
    typer.echo(
        f"{typer.style('Comissions:', bold=True)} "
        f"{data.completed_commissions}/{data.max_comissions}",
        nl=False,
    )
    if data.completed_commissions == data.max_comissions and not data.claimed_comission_reward:
        typer.echo(f" | [{typer.style('X', fg='red')}] Haven't claimed rewards")
    else:
        typer.echo()
    typer.echo(
        f"{typer.style('Used resin cost-halving opportunities:', bold=True)} "
        f"{data.max_resin_discounts - data.remaining_resin_discounts}/{data.max_resin_discounts}"
    )

    typer.echo(
        f"\n{typer.style('Expeditions:', bold=True)} "
        f"{len(data.expeditions)}/{data.max_expeditions}"
    )
    for expedition in data.expeditions:
        seconds = expedition.remaining.seconds
        remaining = f"{seconds // 3600:2}:{seconds % 3600 // 60:02}"
        typer.echo(f" - {expedition.status} | {remaining} remaining - {expedition.character.name}")


@app.command()
@asynchronous
async def wishes(
    limit: int = typer.Option(None, help="The maximum amount of wishes to show"),
    lang: str = typer.Option("en-us", help="The language to use"),
):
    """Get a nicely formatted wish history"""
    async with genshin.GenshinClient() as client:
        client.set_authkey()

        banner_names = await client.get_banner_names(lang=lang)
        longest = max(len(v) for v in banner_names.values())

        async for wish in client.wish_history(limit=limit, lang=lang):
            banner = typer.style(wish.banner_name.ljust(longest), bold=True)
            typer.echo(f"{banner} | {wish.time} - {wish.name} ({'★' * wish.rarity} {wish.type})")


@app.command()
@asynchronous
async def pity():
    """Calculates the amount of pulls until pity"""
    async with genshin.GenshinClient() as client:
        client.set_authkey()

        banners = await client.get_banner_names()
        for banner, name in banners.items():
            # skip the novice banner
            if banner == 100:
                continue

            typer.echo()
            typer.secho(name, fg="yellow")

            accum = 0
            async for wish in client.wish_history(banner):
                accum += 1
                if wish.rarity == 5:
                    a = typer.style(str(90 - accum), bold=True)
                    typer.secho(f"{accum} pulls since a 5*, {a} pulls left until pity")
                    break
            else:
                a = typer.style(str(90 - accum), bold=True)
                typer.secho(f"Never pulled a 5*, at most {a} pulls left until pity")


if __name__ == "__main__":
    app()
