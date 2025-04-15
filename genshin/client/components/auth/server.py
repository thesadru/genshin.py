"""Aiohttp webserver used for captcha solving and verification."""

from __future__ import annotations

import asyncio
import typing
import webbrowser

import aiohttp
from aiohttp import web

from genshin import types
from genshin.models.auth.geetest import (
    MMT,
    MMTResult,
    MMTv4,
    MMTv4Result,
    RiskyCheckMMT,
    RiskyCheckMMTResult,
    SessionMMT,
    SessionMMTResult,
    SessionMMTv4,
    SessionMMTv4Result,
)
from genshin.utility import auth as auth_utility

__all__ = ["PAGES", "enter_code", "launch_webapp", "solve_geetest"]

PAGES: typing.Final[dict[typing.Literal["captcha", "enter-code"], str]] = {
    "captcha": """
    <!DOCTYPE html>
    <head>
      <meta name="referrer" content="no-referrer"/>
    </head>
    <html>
      <body></body>
      <script src="./gt/v{gt_version}.js"></script>
      <script>
        const geetestVersion = {gt_version};
        const initGeetest = geetestVersion === 3 ? window.initGeetest : window.initGeetest4;
        fetch("/mmt")
          .then((response) => response.json())
          .then((mmt) => {
            const initParams = geetestVersion === 3 ? {
              gt: mmt.gt,
              challenge: mmt.challenge,
              new_captcha: mmt.new_captcha,
              api_server: "{api_server}",
              https: /^https/i.test(window.location.protocol),
              product: "bind",
              lang: "{lang}",
            } : {
              captchaId: mmt.gt,
              riskType: mmt.risk_type,
              userInfo: mmt.session_id ? JSON.stringify({
                mmt_key: mmt.session_id
              }) : undefined,
              api_server: "{api_server}",
              product: "bind",
              language: "{lang}",
            };
            initGeetest(
              initParams,
              (captcha) => {
                captcha.onReady(() => {
                  geetestVersion == 3 ? captcha.verify() : captcha.showCaptcha();
                });
                captcha.onSuccess(() => {
                  fetch("/send-data", {
                    method: "POST",
                    body: JSON.stringify({
                      ...(mmt.session_id && {session_id: mmt.session_id}),
                      ...(mmt.check_id && {check_id: mmt.check_id}),
                      ...captcha.getValidate()
                    }),
                  }).then(() => window.close());
                  document.body.innerHTML = "You may now close this window.";
                });
              }
            )
          });
      </script>
    </html>
    """,
    "enter-code": """
    <!DOCTYPE html>
    <html>
      <body>
        <input id="code" type="number">
        <button id="verify">Send</button>
      </body>
      <script>
        document.getElementById("verify").onclick = () => {
          fetch("/send-data", {
            method: "POST",
            body: JSON.stringify({
              code: document.getElementById("code").value
            }),
          });
          document.body.innerHTML = "You may now close this window.";
        };
      </script>
    </html>
    """,
}


GT_V3_URL = "https://static.geetest.com/static/js/gt.0.5.0.js"
GT_V4_URL = "https://static.geetest.com/v4/gt4.js"


@typing.overload
async def launch_webapp(
    page: typing.Literal["captcha"],
    *,
    mmt: typing.Union[MMT, MMTv4, SessionMMT, SessionMMTv4, RiskyCheckMMT],
    lang: str = ...,
    api_server: str = ...,
    port: int = ...,
) -> typing.Union[MMTResult, MMTv4Result, SessionMMTResult, SessionMMTv4Result, RiskyCheckMMTResult]: ...
@typing.overload
async def launch_webapp(
    page: typing.Literal["enter-code"],
    *,
    mmt: None = ...,
    lang: None = ...,
    api_server: None = ...,
    port: int = ...,
) -> str: ...
async def launch_webapp(
    page: typing.Literal["captcha", "enter-code"],
    *,
    mmt: typing.Optional[typing.Union[MMT, MMTv4, SessionMMT, SessionMMTv4, RiskyCheckMMT]] = None,
    lang: typing.Optional[str] = None,
    api_server: typing.Optional[str] = None,
    port: int = 5000,
) -> typing.Union[MMTResult, MMTv4Result, SessionMMTResult, SessionMMTv4Result, RiskyCheckMMTResult, str]:
    """Create and run a webapp to solve captcha or enter a verification code."""
    routes = web.RouteTableDef()
    future: asyncio.Future[typing.Any] = asyncio.Future()

    @routes.get("/")
    async def index(request: web.Request) -> web.StreamResponse:
        body = PAGES[page]
        body = body.replace("{gt_version}", "4" if isinstance(mmt, MMTv4) else "3")
        body = body.replace("{api_server}", api_server or "api-na.geetest.com")
        body = body.replace("{lang}", lang or "en")
        return web.Response(body=body, content_type="text/html")

    @routes.get("/gt/{version}.js")
    async def gt(request: web.Request) -> web.StreamResponse:
        version = request.match_info.get("version", "v3")
        gt_url = GT_V4_URL if version == "v4" else GT_V3_URL

        async with aiohttp.ClientSession() as session:
            r = await session.get(gt_url)
            content = await r.read()

        return web.Response(body=content, content_type="text/javascript")

    @routes.get("/mmt")
    async def mmt_endpoint(request: web.Request) -> web.Response:
        return web.json_response(mmt.model_dump() if mmt else {})

    @routes.post("/send-data")
    async def send_data_endpoint(request: web.Request) -> web.Response:
        result = await request.json()
        if "code" in result:
            result = result["code"]
        else:
            if isinstance(mmt, RiskyCheckMMT):
                result = RiskyCheckMMTResult(**result)
            elif isinstance(mmt, SessionMMT):
                result = SessionMMTResult(**result)
            elif isinstance(mmt, SessionMMTv4):
                result = SessionMMTv4Result(**result)
            elif isinstance(mmt, MMT):
                result = MMTResult(**result)
            elif isinstance(mmt, MMTv4):
                result = MMTv4Result(**result)

        future.set_result(result)
        return web.Response(status=204)

    app = web.Application()
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host="localhost", port=port)
    print(f"Opening http://localhost:{port} in browser...")  # noqa
    webbrowser.open_new_tab(f"http://localhost:{port}")

    await site.start()

    try:
        data = await future
    finally:
        await asyncio.sleep(0.3)
        await runner.shutdown()
        await runner.cleanup()

    return data


@typing.overload
async def solve_geetest(
    mmt: RiskyCheckMMT,
    *,
    lang: types.Lang = ...,
    api_server: str = ...,
    port: int = ...,
) -> RiskyCheckMMTResult: ...
@typing.overload
async def solve_geetest(
    mmt: SessionMMT,
    *,
    lang: types.Lang = ...,
    api_server: str = ...,
    port: int = ...,
) -> SessionMMTResult: ...
@typing.overload
async def solve_geetest(
    mmt: MMT,
    *,
    lang: types.Lang = ...,
    api_server: str = ...,
    port: int = ...,
) -> MMTResult: ...
@typing.overload
async def solve_geetest(
    mmt: SessionMMTv4,
    *,
    lang: types.Lang = ...,
    api_server: str = ...,
    port: int = ...,
) -> SessionMMTv4Result: ...
@typing.overload
async def solve_geetest(
    mmt: MMTv4,
    *,
    lang: types.Lang = ...,
    api_server: str = ...,
    port: int = ...,
) -> MMTv4Result: ...
async def solve_geetest(
    mmt: typing.Union[MMT, MMTv4, SessionMMT, SessionMMTv4, RiskyCheckMMT],
    *,
    lang: types.Lang = "en-us",
    api_server: str = "api-na.geetest.com",
    port: int = 5000,
) -> typing.Union[MMTResult, MMTv4Result, SessionMMTResult, SessionMMTv4Result, RiskyCheckMMTResult]:
    """Start a web server and manually solve geetest captcha."""
    geetest_lang = auth_utility.lang_to_geetest_lang(lang)
    return await launch_webapp(
        "captcha",
        mmt=mmt,
        lang=geetest_lang,
        api_server=api_server,
        port=port,
    )


async def enter_code(*, port: int = 5000) -> str:
    """Get email or phone number verification code from user."""
    return await launch_webapp("enter-code", port=port)
