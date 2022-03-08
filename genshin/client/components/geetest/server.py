"""Aiohttp webserver used for login."""
from __future__ import annotations

import asyncio
import typing
import webbrowser

from aiohttp import web

from genshin.utility import geetest

from . import client


async def login_with_app(client: client.GeetestClient, account: str, password: str, *, port: int = 5000) -> typing.Any:
    """Create and run an application for handling login."""
    routes = web.RouteTableDef()
    future: asyncio.Future[typing.Any] = asyncio.Future()

    mmt_key: str = ""

    @routes.get("/")
    async def index(request: web.Request) -> web.StreamResponse:
        return web.FileResponse(geetest.INDEX_PATH)

    @routes.get("/gt.js")
    async def gt(request: web.Request) -> web.StreamResponse:
        return web.FileResponse(geetest.GT_PATH)

    @routes.get("/mmt")
    async def mmt_endpoint(request: web.Request) -> web.Response:
        nonlocal mmt_key

        mmt = await geetest.create_mmt()
        mmt_key = mmt["mmt_key"]
        return web.json_response(mmt)

    @routes.post("/login")
    async def login_endpoint(request: web.Request) -> web.Response:
        body = await request.json()

        data = await client.login_with_geetest(
            account=account,
            password=password,
            mmt_key=mmt_key,
            geetest=body,
        )
        future.set_result(data)

        return web.json_response(data)

    app = web.Application()
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host="localhost", port=port)
    print(f"Opened browser in http://localhost:{port}")  # noqa
    webbrowser.open_new_tab(f"http://localhost:{port}")

    await site.start()

    data = await future

    await asyncio.sleep(0.3)
    await runner.shutdown()

    return data
