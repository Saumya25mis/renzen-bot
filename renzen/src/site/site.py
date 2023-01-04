"""Expose endpoint for aiohttp server"""

import json
import logging
import os
from typing import Optional
import dataclasses

from aiohttp import web
import aiohttp_cors  # type: ignore
from src.common import queue_utils
from src.common import db_utils


logger = logging.getLogger(__name__)

CURRENT_ENVIRONMENT = os.getenv("CURRENT_ENVIRONMENT")


async def handle(request: web.Request) -> web.Response:
    """Health check response."""
    response_obj = {"status": "success"}
    print(response_obj)
    return web.Response(text=json.dumps(response_obj))


async def forward(request: web.Request) -> web.Response:
    """forward check response."""

    logger.info("Received forward request.")

    request_content = await request.json()

    print(f"{request_content=}")

    login_user_relation: Optional[db_utils.LoginCodes] = db_utils.query_db_by_code(
        request_content["login-code"]
    )

    if not login_user_relation:
        response_obj = {"status": "FAILURE forward NO MATCHING USER ID"}
        return web.Response(text=json.dumps(response_obj))

    user_id = int(login_user_relation.discord_user_id)
    snippet = request_content["snippet"]
    url = request_content["URL"]
    title = request_content["title"]

    db_id = db_utils.save_snippet_to_db(url, snippet, user_id, title)

    queue_utils.send_message(message={"request_content": str(db_id)})
    response_obj = {"status": f"success forward {db_id}"}

    return web.Response(text=json.dumps(response_obj))


async def check_valid_code(request: web.Request) -> web.Response:
    """Used by chrome extension to check if user can login with code."""

    logger.info("Received valid code request.")

    request_text = await request.text()
    result = db_utils.query_db_by_code(str(request_text))

    if result:
        return web.Response(text="valid")
    return web.Response(text="invalid")


async def get_snippets(request: web.Request) -> web.Response:
    """Return snippets when provided login code."""

    logger.info("Received valid code request.")

    request_json = await request.json()
    print(f"{request_json=}")
    code_query = db_utils.query_db_by_code(request_json["login-code"])

    if code_query:
        snippets = db_utils.search_urls_by_user(code_query.discord_user_id)
        snippets_dict = [dataclasses.asdict(snippet) for snippet in snippets]
        return web.Response(text=json.dumps(snippets_dict, default=str))

    return web.Response(text="invalid", headers={"Access-Control-Allow-Origin": "*"})


app = web.Application()

cors = aiohttp_cors.setup(app)
resource = cors.add(app.router.add_resource("/get_snippets"))

route = cors.add(
    resource.add_route("POST", get_snippets),
    {
        "http://localhost:3000": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Custom-Server-Header",),
            allow_headers=("X-Requested-With", "Content-Type"),
            max_age=10,
        ),
        "*": aiohttp_cors.ResourceOptions(
            expose_headers=("X-Custom-Server-Header",),
            allow_headers=(
                "X-Requested-With",
                "Content-Type",
                "Access-Control-Allow-Origin",
            ),
            max_age=10,
        ),
    },
)

app.router.add_get("/", handle)
app.router.add_get("/forward", forward)
app.router.add_route("POST", "/forward", forward)
app.router.add_route("GET", "/valid_code", check_valid_code)
# app.router.add_route("POST", "/get_snippets", get_snippets)

web.run_app(app, port=80, host="0.0.0.0")
