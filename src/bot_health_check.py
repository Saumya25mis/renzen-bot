"""Expose endpoint for aiohttp server"""

import json
from aiohttp import web


async def handle(
    request: web.Request,
) -> web.Response:  # pylint:disable=unused-argument
    """Health check response."""
    response_obj = {"status": "success"}
    return web.Response(text=json.dumps(response_obj))


app = web.Application()
app.router.add_get("/", handle)

web.run_app(app, port=80)
