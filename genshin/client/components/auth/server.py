"""Aiohttp webserver used for captcha solving and verification."""

from __future__ import annotations

import asyncio
import typing
import webbrowser

import aiohttp
from aiohttp import web

from genshin.models.auth.geetest import (
    MMT,
    MMTv4,
    RiskyCheckMMT,
    MMTResult,
    MMTv4Result,
    SessionMMT,
    SessionMMTv4,
    SessionMMTResult,
    SessionMMTv4Result,
    RiskyCheckMMTResult,
)
from genshin.utility import auth as auth_utility

__all__ = ["PAGES", "enter_code", "launch_webapp", "solve_geetest"]

PAGES: typing.Final[typing.Dict[typing.Literal["captcha", "captcha-v4", "enter-code"], str]] = {
    "captcha": """
    <!DOCTYPE html>
    <html>
      <body></body>
      <script src="./gt/v3.js"></script>
      <script>
        fetch("/mmt")
          .then((response) => response.json())
          .then((mmt) =>
            window.initGeetest(
              {
                gt: mmt.gt,
                challenge: mmt.challenge,
                new_captcha: mmt.new_captcha,
                api_server: '{api_server}',
                https: /^https/i.test(window.location.protocol),
                product: "bind",
                lang: '{lang}',
              },
              (captcha) => {
                captcha.onReady(() => {
                  captcha.verify();
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
          );
        if ({proxy_geetest}) {
          Object.defineProperty(HTMLScriptElement.prototype, 'src', {
            get: function() {
              return this.getAttribute('src')
            },
            set: function(url) {
              const proxyPrefixes = [
                /^http:\\/\\/.*\\.geevisit\\.com/,
                /^{api_server}/
              ];
              const prefix = proxyPrefixes.find((prefix) => url.match(prefix));
              if (prefix) {
                console.debug('[Proxy] Request URL override:');
                console.debug('From: ' + url);
                newUrl = new URL(url);
                newUrl.searchParams.set('url', newUrl.origin + newUrl.pathname);
                url = window.location.origin + '/proxy' + newUrl.search;
                console.debug('To: ' + url);
              }
              this.setAttribute('src', url);
            }
          });
        }
      </script>
    </html>
    """,
    "captcha-v4": """
    <!DOCTYPE html>
    <html>
      <body></body>
      <script src="./gt/v4.js"></script>
      <script>
        fetch("/mmt")
          .then((response) => response.json())
          .then((mmt) =>
            window.initGeetest4(
              {
                captchaId: mmt.gt,
                riskType: mmt.risk_type,
                userInfo: mmt.session_id ? JSON.stringify({
                  mmt_key: mmt.session_id
                }) : undefined,
                api_server: '{api_server}',
                product: "bind",
                language: '{lang}',
              },
              (captcha) => {
                captcha.onReady(() => {
                  captcha.showCaptcha();
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
          );
        if ({proxy_geetest}) {
          Object.defineProperty(HTMLScriptElement.prototype, 'src', {
            get: function() {
              return this.getAttribute('src')
            },
            set: function(url) {
              const proxyPrefixes = [
                /^http:\\/\\/.*\\.geevisit\\.com/,
                /^{api_server}/
              ];
              const prefix = proxyPrefixes.find((prefix) => url.match(prefix));
              if (prefix) {
                console.debug('[Proxy] Request URL override:');
                console.debug('From: ' + url);
                newUrl = new URL(url);
                newUrl.searchParams.set('url', newUrl.origin + newUrl.pathname);
                url = window.location.origin + '/proxy' + newUrl.search;
                console.debug('To: ' + url);
              }
              this.setAttribute('src', url);
            }
          });
        }
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
    page: typing.Literal["captcha", "captcha-v4"],
    *,
    mmt: typing.Union[MMT, MMTv4, SessionMMT, SessionMMTv4, RiskyCheckMMT],
    lang: str = "en",
    api_server: str = "api-na.geetest.com",
    proxy_geetest: bool = False,
    port: int = 5000,
) -> typing.Union[MMTResult, MMTv4Result, SessionMMTResult, SessionMMTv4Result, RiskyCheckMMTResult]: ...
@typing.overload
async def launch_webapp(
    page: typing.Literal["enter-code"],
    *,
    mmt: None = None,
    lang: None = None,
    api_server: None = None,
    proxy_geetest: None = None,
    port: int = 5000,
) -> str: ...
async def launch_webapp(
    page: typing.Literal["captcha", "captcha-v4", "enter-code"],
    *,
    mmt: typing.Optional[typing.Union[MMT, MMTv4, SessionMMT, SessionMMTv4, RiskyCheckMMT]] = None,
    lang: typing.Optional[str] = None,
    api_server: typing.Optional[str] = None,
    proxy_geetest: typing.Optional[bool] = None,
    port: int = 5000,
) -> typing.Union[MMTResult, MMTv4Result, SessionMMTResult, SessionMMTv4Result, RiskyCheckMMTResult, str]:
    """Create and run a webapp to solve captcha or enter a verification code."""
    routes = web.RouteTableDef()
    future: asyncio.Future[typing.Any] = asyncio.Future()

    @routes.get("/")
    async def index(request: web.Request) -> web.StreamResponse:
        body = PAGES[page]
        body = body.replace("{api_server}", api_server or "api-na.geetest.com")
        body = body.replace("{proxy_geetest}", str(proxy_geetest or False).lower())
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

    @routes.get("/proxy")
    async def proxy(request: web.Request) -> web.Response:
        params = dict(request.query)
        url = params.pop("url", None)
        if not url:
            return web.Response(status=400)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                content = await r.read()

        return web.Response(body=content, status=r.status, content_type="text/javascript")

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
    lang: str = "en-us",
    api_server: str = "api-na.geetest.com",
    proxy_geetest: bool = False,
    port: int = 5000,
) -> RiskyCheckMMTResult: ...
@typing.overload
async def solve_geetest(
    mmt: SessionMMT,
    *,
    lang: str = "en-us",
    api_server: str = "api-na.geetest.com",
    proxy_geetest: bool = False,
    port: int = 5000,
) -> SessionMMTResult: ...
@typing.overload
async def solve_geetest(
    mmt: MMT,
    *,
    lang: str = "en-us",
    api_server: str = "api-na.geetest.com",
    proxy_geetest: bool = False,
    port: int = 5000,
) -> MMTResult: ...
@typing.overload
async def solve_geetest(
    mmt: SessionMMTv4,
    *,
    lang: str = "en-us",
    api_server: str = "api.geetest.com",
    proxy_geetest: bool = False,
    port: int = 5000,
) -> SessionMMTv4Result: ...
@typing.overload
async def solve_geetest(
    mmt: MMTv4,
    *,
    lang: str = "en-us",
    api_server: str = "api.geetest.com",
    proxy_geetest: bool = False,
    port: int = 5000,
) -> MMTv4Result: ...
async def solve_geetest(
    mmt: typing.Union[MMT, MMTv4, SessionMMT, SessionMMTv4, RiskyCheckMMT],
    *,
    lang: str = "en-us",
    api_server: str = "api-na.geetest.com",
    proxy_geetest: bool = False,
    port: int = 5000,
) -> typing.Union[MMTResult, MMTv4Result, SessionMMTResult, SessionMMTv4Result, RiskyCheckMMTResult]:
    """Start a web server and manually solve geetest captcha."""
    use_v4 = isinstance(mmt, MMTv4)
    lang = auth_utility.lang_to_geetest_lang(lang)
    return await launch_webapp(
        "captcha-v4" if use_v4 else "captcha",
        mmt=mmt,
        lang=lang,
        api_server=api_server,
        proxy_geetest=proxy_geetest,
        port=port,
    )


async def enter_code(*, port: int = 5000) -> str:
    """Get email or phone number verification code from user."""
    return await launch_webapp("enter-code", port=port)
