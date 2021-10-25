from enum import Enum
from typing import Annotated, List, Literal, Type, Union, cast

import genshin
from fastapi import FastAPI, Query
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


@app.get("/card/{hoyolab_uid}", response_model=genshin.models.RecordCard)
async def hoyolab_user(hoyolab_uid: int, lang: Lang = None):
    return await client.get_record_card(hoyolab_uid, lang=lang)


@app.get("/user/{uid}", response_model=genshin.models.UserStats)
async def user(uid: int, lang: Lang = None):
    return await client.get_user(uid, lang=lang)


@app.get("/user/{uid}/abyss", response_model=genshin.models.SpiralAbyss)
async def abyss(uid: int, previous: bool = False):
    return await client.get_spiral_abyss(uid, previous=previous)


@app.get("/user/{uid}/notes", response_model=genshin.models.Notes)
async def notes(uid: int, lang: Lang = None):
    return await client.get_notes(uid, lang=lang)


@app.get("/user/{uid}/activities", response_model=genshin.models.Activities)
async def activities(uid: int, lang: Lang = None):
    return await client.get_activities(uid, lang=lang)


@app.get("/user/{uid}/partial", response_model=genshin.models.PartialUserStats)
async def partial_user(uid: int, lang: Lang = None):
    return await client.get_partial_user(uid, lang=lang)


@app.get("/user/{uid}/full", response_model=genshin.models.FullUserStats)
async def full_user(uid: int, lang: Lang = None):
    return await client.get_full_user(uid, lang=lang)


@app.get("/wish", response_model=List[genshin.models.Wish])
async def wish(
    authkey: str,
    banner: Literal["100", "200", "301", "302"] = None,
    size: int = 20,
    end_id: int = 0,
    lang: Lang = None,
):
    # parse the banner from a string
    if banner is not None:
        bt = cast(genshin.models.BannerType, int(banner))
    else:
        bt = None

    paginator = client.wish_history(bt, limit=size, lang=lang, authkey=authkey, end_id=end_id)
    return await paginator.flatten()


@app.get(
    "/transaction",
    response_model=List[Union[genshin.models.Transaction, genshin.models.ItemTransaction]],
)
async def transaction(
    authkey: str,
    kind: genshin.models.TransactionKind = None,
    size: int = 20,
    end_id: int = 0,
    lang: Lang = None,
):
    paginator = client.transaction_log(kind, limit=size, lang=lang, authkey=authkey, end_id=end_id)
    return await paginator.flatten()


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
