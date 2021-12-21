from enum import Enum
from typing import List, Literal, Type, Union, cast

import genshin
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse, RedirectResponse

__all__ = ["app"]

app = FastAPI()
client = genshin.MultiCookieClient(debug=True)

Lang: Type[str] = Enum("Lang", {k: k for k in genshin.LANGS}, type=str)


@app.on_event("startup")
async def on_startup():
    client.set_cookies("cookies.json")
    client.set_cache(1024, ttl=3600)


@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse("/docs")


@app.get("/card/{hoyolab_uid}", response_model=genshin.models.genshin.RecordCard, tags=["chronicle"])
async def hoyolab_user(hoyolab_uid: int, lang: Lang = None):
    return await client.get_record_card(hoyolab_uid, lang=lang)


@app.get("/user/{uid}", response_model=genshin.models.genshin.UserStats, tags=["chronicle"])
async def user(uid: int, lang: Lang = None):
    return await client.get_user(uid, lang=lang)


@app.get("/user/{uid}/abyss", response_model=genshin.models.genshin.SpiralAbyss, tags=["chronicle"])
async def abyss(uid: int, previous: bool = False):
    return await client.get_spiral_abyss(uid, previous=previous)


@app.get("/user/{uid}/notes", response_model=genshin.models.genshin.Notes, tags=["chronicle"])
async def notes(uid: int, lang: Lang = None):
    return await client.get_notes(uid, lang=lang)


@app.get("/user/{uid}/activities", response_model=genshin.models.genshin.Activities, tags=["chronicle"])
async def activities(uid: int, lang: Lang = None):
    return await client.get_activities(uid, lang=lang)


@app.get("/user/{uid}/partial", response_model=genshin.models.genshin.PartialUserStats, tags=["chronicle"])
async def partial_user(uid: int, lang: Lang = None):
    return await client.get_partial_user(uid, lang=lang)


@app.get("/user/{uid}/full", response_model=genshin.models.genshin.FullUserStats, tags=["chronicle"])
async def full_user(uid: int, lang: Lang = None):
    return await client.get_full_user(uid, lang=lang)


@app.get("/wish", response_model=List[genshin.models.genshin.Wish], tags=["remote"])
async def wish(
    authkey: str,
    banner: Literal["100", "200", "301", "302"] = None,
    size: int = 20,
    end_id: int = 0,
    lang: Lang = None,
):
    # parse the banner from a string
    if banner is not None:
        bt = cast(genshin.models.genshin.BannerType, int(banner))
    else:
        bt = None

    paginator = client.wish_history(bt, limit=size, lang=lang, authkey=authkey, end_id=end_id)
    return await paginator.flatten()


@app.get(
    "/transaction",
    response_model=List[Union[genshin.models.genshin.Transaction, genshin.models.genshin.ItemTransaction]],
    tags=["remote"],
)
async def transaction(
    authkey: str,
    kind: genshin.models.genshin.TransactionKind = "primogem",
    size: int = 20,
    end_id: int = 0,
    lang: Lang = None,
):
    paginator = client.transaction_log(kind, limit=size, lang=lang, authkey=authkey, end_id=end_id)
    return await paginator.flatten()


@app.get(
    "/calculator/characters",
    response_model=List[genshin.models.genshin.CalculatorCharacter],
    tags=["calculator"],
)
async def calculator_characters(query: str = None, lang: Lang = None):
    return await client.get_calculator_characters(query=query, lang=lang)


@app.get(
    "/calculator/weapons", response_model=List[genshin.models.genshin.CalculatorWeapon], tags=["calculator"]
)
async def calculator_weapons(query: str = None, lang: Lang = None):
    return await client.get_calculator_weapons(query=query, lang=lang)


@app.get(
    "/calculator/artifacts",
    response_model=List[genshin.models.genshin.CalculatorArtifact],
    tags=["calculator"],
)
async def calculator_artifacts(query: str = None, pos: int = 1, lang: Lang = None):
    return await client.get_calculator_artifacts(query=query, pos=pos, lang=lang)


@app.get(
    "/calculator/characters/{character_id}/talents",
    response_model=List[genshin.models.genshin.CalculatorTalent],
    tags=["calculator"],
)
async def calculator_character_talents(character_id: int, lang: Lang = None):
    return await client.get_character_talents(character_id)


@app.get(
    "/calculator/artifacts/{artifact_id}/set",
    response_model=List[genshin.models.genshin.CalculatorArtifact],
    tags=["calculator"],
)
async def calculator_artifact_set(artifact_id: int, lang: Lang = None):
    return await client.get_complete_artifact_set(artifact_id, lang=lang)


@app.exception_handler(genshin.GenshinException)
async def handle_genshin_exception(request: Request, exc: genshin.GenshinException):
    if isinstance(exc, genshin.AccountNotFound):
        status_code = 404
    elif isinstance(exc, genshin.DataNotPublic):
        status_code = 403
    elif isinstance(exc, genshin.TooManyRequests):
        status_code = 429
    else:
        status_code = 400

    content = {"message": exc.msg, "original": exc.original, "retcode": exc.retcode}
    if type(exc) != genshin.GenshinClient:
        content["type"] = type(exc).__name__

    return JSONResponse(content, status_code)
