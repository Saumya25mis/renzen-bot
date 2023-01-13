# pylint: disable=line-too-long

"""Expose endpoint for aiohttp server

Used by Chrome Extension and VS code Extension
"""

import dataclasses
import json
import logging
import os
from typing import Any, Dict

# import requests
import aiohttp
import aiohttp_cors  # type: ignore

# import jwt  # type: ignore
from aiohttp import web
from src.common import db_utils, queue_utils
from src.common.api_types import (
    ForwardRequest,
    GetSnippetsRequest,
    GithubAccessTokenResponse,
    StarRequest,
)

# from urllib import parse


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CURRENT_ENVIRONMENT = os.getenv("CURRENT_ENVIRONMENT")
GITHUB_LOCAL_OAUTH_CLIENT_SECRET = os.getenv("GITHUB_LOCAL_OAUTH_CLIENT_SECRET")
GITHUB_LOCAL_OAUTH_CLIENT_ID = "b981ba10feff55da4f93"
GITHUB_LOCAL_OAUTH_REDIRECT_URI = "http://localhost:81/api/auth/github"
GITHUB_LOCAL_OAUTH_PATH = "/"


async def aws_health_check(request: web.Request) -> web.Response:
    """Health check response."""
    response_obj = {"status": "success"}
    # print(response_obj)
    return web.Response(text=json.dumps(response_obj))


async def chrome_ext_forward(request: web.Request) -> web.Response:
    """forward check response."""

    logger.warning("Received forward request.")

    # get request object
    request_content = await request.json()
    logger.warning(f"{request_content=}")
    forward_request: ForwardRequest = ForwardRequest(**request_content)

    # get renzen user id from code
    renzen_user_info = db_utils.get_renzen_user_by_code(forward_request.login_code)

    if not renzen_user_info:
        api_response_obj = {"status": "FAILURE forward NO MATCHING USER ID"}
    else:

        # save snippet to database
        forward_save_object = {
            "renzen_user_id": str(renzen_user_info.renzen_user_id),
            "snippet": forward_request.snippet,
            "url": forward_request.url,
            "title": forward_request.title,
        }
        db_id = db_utils.save_snippet_to_db(**forward_save_object)

        # save snippet id to queue (for pickup by listeners (bot))
        forward_queue_object = {"request_content": str(db_id)}
        queue_utils.send_message(message=forward_queue_object)

        api_response_obj = {"status": f"success forward snipped id: {db_id}"}

    return web.Response(text=json.dumps(api_response_obj, default=str))


async def vs_ext_get_snippets(request: web.Request) -> web.Response:
    """Return snippets when provided login code."""

    logger.warning("Received get snippets code request.")

    request_json = await request.json()
    logger.warning(f"vs_ext_get_snippets {request_json=}")
    get_snippets_request: GetSnippetsRequest = GetSnippetsRequest(**request_json)

    renzen_user_info = db_utils.get_renzen_user_by_code(get_snippets_request.login_code)

    if renzen_user_info:

        starred_snippets = db_utils.vs_ext_get_mapped_paths_to_snippets(
            renzen_user_id=renzen_user_info.renzen_user_id,
            fetch_url=get_snippets_request.fetch_url,
        )
        all_snippets = db_utils.vs_ext_get_all_user_snippets(
            renzen_user_info.renzen_user_id
        )

        api_response_obj: Dict[Any, Any] = {
            "all_dicts": [dataclasses.asdict(snippet) for snippet in all_snippets],
            "starred_dicts": [
                dataclasses.asdict(snippet) for snippet in starred_snippets
            ],
        }

    else:
        api_response_obj = {"error": "Code does not correspond to user."}

    return web.Response(text=json.dumps(api_response_obj, default=str))


async def vs_ext_star(request: web.Request) -> web.Response:
    """Associates file page with snippet."""

    logger.warning("Received star request.")

    request_json = await request.json()
    logger.warning(f"{request_json=}")

    star_request: StarRequest = StarRequest(**request_json)

    result = db_utils.star(
        renzen_user_id=star_request.renzen_user_id,
        path=star_request.page_path,
        snippet_id=star_request.snippet_id,
        fetch_url=star_request.fetch_url,
        req_type=star_request.req_type,
        star_id=star_request.star_id,
    )
    return web.Response(
        text=json.dumps(result, default=str),
    )


app = web.Application()
cors = aiohttp_cors.setup(
    app,
    defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            max_age=10,
        ),
    },
)


async def get_github_user(code: str) -> Any:
    """Get bearer token and fetch user."""

    # step 2 Users are redirected back to your site by GitHub
    async with aiohttp.request(
        method="post",
        url=f"https://github.com/login/oauth/access_token?client_id={GITHUB_LOCAL_OAUTH_CLIENT_ID}&client_secret={GITHUB_LOCAL_OAUTH_CLIENT_SECRET}&code={code}",
        headers={"Accept": "application/json"},
    ) as res:

        res_json = await res.json()
        logger.warning(res_json)

        access_token_response = GithubAccessTokenResponse(**res_json)

        # 3. Use the access token to access the API
        async with aiohttp.request(
            method="get",
            url="https://api.github.com/user",
            headers={
                "Authorization": f"{access_token_response.token_type} {access_token_response.access_token}"
            },
        ) as user_data:

            # do something with user data

            return await user_data.json()


async def github_oauth(request: web.Request) -> None:
    """Github Oauth."""

    logger.warning("Received github oauth request.")

    code = request.url.query["code"]
    path = request.url.query["path"]

    user_data = await get_github_user(code=code)

    # temp_secret = "temp_secret"

    # token = jwt.encode(user_data, key=temp_secret)

    # redirect?
    # temporary query encode
    # raise web.HTTPFound(path + parse.urlencode({"token": token}), text="HELLO")
    raise web.HTTPFound(path)


resource = cors.add(app.router.add_resource("/get_snippets"))
cors.add(resource.add_route("POST", vs_ext_get_snippets))

resource = cors.add(app.router.add_resource("/star"))
cors.add(resource.add_route("POST", vs_ext_star))

resource = cors.add(app.router.add_resource("/forward"))
cors.add(resource.add_route("POST", chrome_ext_forward))

resource = cors.add(app.router.add_resource("/"))
cors.add(resource.add_route("GET", aws_health_check))

resource = cors.add(app.router.add_resource("/api/auth/github"))
cors.add(resource.add_route("GET", github_oauth))

web.run_app(app, port=80, host="0.0.0.0")
