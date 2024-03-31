"""Aiohttp webserver used for captcha solving and email verification."""

from __future__ import annotations

import asyncio
import typing
import webbrowser

import aiohttp
from aiohttp import web

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
                gt: mmt.data.gt,
                challenge: mmt.data.challenge,
                new_captcha: mmt.data.new_captcha,
                api_server: "api-na.geetest.com",
                https: /^https/i.test(window.location.protocol),
                product: "bind",
                lang: "en",
              },
              (captcha) => {
                captcha.onReady(() => {
                  captcha.verify();
                });
                captcha.onSuccess(() => {
                  fetch("/send-data", {
                    method: "POST",
                    body: JSON.stringify({
                      session_id: mmt.session_id,
                      data: captcha.getValidate()
                    }),
                  }).then(() => window.close());
                  document.body.innerHTML = "You may now close this window.";
                });
              }
            )
          );
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
                captchaId: mmt.data.gt,
                riskType: mmt.data.risk_type,
                userInfo: JSON.stringify({
                  mmt_key: mmt.session_id
                }),
                product: "bind",
                language: "en",
              },
              (captcha) => {
                captcha.onReady(() => {
                  captcha.showCaptcha();
                });
                captcha.onSuccess(() => {
                  fetch("/send-data", {
                    method: "POST",
                    body: JSON.stringify({
                      session_id: mmt.session_id,
                      data: captcha.getValidate()
                    }),
                  }).then(() => window.close());
                  document.body.innerHTML = "You may now close this window.";
                });
              }
            )
          );
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


async def launch_webapp(
    page: typing.Literal["captcha", "captcha-v4", "enter-code"],
    *,
    port: int = 5000,
    mmt: typing.Optional[typing.Dict[str, typing.Any]] = None,
) -> typing.Any:
    """Create and run a webapp to solve captcha or send verification code."""
    routes = web.RouteTableDef()
    future: asyncio.Future[typing.Any] = asyncio.Future()

    @routes.get("/")
    async def index(request: web.Request) -> web.StreamResponse:
        return web.Response(body=PAGES[page], content_type="text/html")

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
        return web.json_response(mmt)

    @routes.post("/send-data")
    async def send_data_endpoint(request: web.Request) -> web.Response:
        body = await request.json()
        future.set_result(body)

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


async def solve_geetest(
    mmt: typing.Dict[str, typing.Any],
    *,
    port: int = 5000,
) -> typing.Dict[str, typing.Any]:
    """Solve a geetest captcha manually.

    The function will automatically detect geetest version
    using the `use_v4` key in the `mmt` dictionary.
    """
    use_v4 = mmt["data"].get("use_v4", False)
    return await launch_webapp("captcha-v4" if use_v4 else "captcha", port=port, mmt=mmt)


async def enter_code(*, port: int = 5000) -> str:
    """Get email or phone number verification code from user."""
    data = await launch_webapp("enter-code", port=port)
    return data["code"]
