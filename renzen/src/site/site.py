# pylint: disable=line-too-long

"""Expose endpoint for aiohttp server

Used by Chrome Extension and VS code Extension
"""

import dataclasses
import json
import logging
from typing import Any, Dict
from urllib import parse

# import requests
import aiohttp
import aiohttp_cors  # type: ignore
import jwt  # type: ignore
from aiohttp import web
from src.common import constants, db_utils, queue_utils, secret_utils
from src.common.api_types import (
    ForwardRequest,
    GetSnippetsRequest,
    GithubAccessTokenResponse,
    StarRequest,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def privacy_policy_page(request: web.Request) -> web.Response:
    """Health check response."""
    response_obj = {"status": "success"}
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

    # CHECK HEADER
    auth_header = request.headers["Authorization"]
    logger.warning(f"{auth_header=}")
    to_decode = auth_header.split(" ")[1]
    logger.warning(f"{to_decode=}")
    token = jwt.decode(to_decode, secret_utils.JWT_SECRET, algorithms=["HS256"])  # type: ignore

    logger.warning(f"{token=}")

    renzen_user_info = db_utils.get_renzen_user_by_username(token["renzen_user_name"])

    logger.warning("Received get snippets code request.")

    request_json = await request.json()
    logger.warning(f"vs_ext_get_snippets {request_json=}")
    get_snippets_request: GetSnippetsRequest = GetSnippetsRequest(**request_json)

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
        api_response_obj = {"error": "Something went wrong."}

    return web.Response(text=json.dumps(api_response_obj, default=str))


async def vs_ext_star(request: web.Request) -> web.Response:
    """Associates file page with snippet."""

    # CHECK HEADER

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
        url=f"https://github.com/login/oauth/access_token?client_id={constants.GITHUB_CLIENT_ID}&client_secret={secret_utils.GITHUB_OAUTH_CLIENT_SECRET}&code={code}",
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

            return await user_data.json()


GITHUB_LOCAL_CALLBACK_URI = "http://localhost:81/"


async def github_oauth(request: web.Request) -> None:
    """Github Oauth. Returns redirect with one-time code to get jwt"""

    logger.warning("Received github oauth request.")
    logger.warning(request.url.human_repr())

    converted_path = parse.parse_qs(request.url.query_string)
    logger.warning(f"First parse: {converted_path=}")

    # HACKY
    # if "vscode" in converted_path["path"][0]:
    #     converted_path = parse.parse_qs(converted_path["path"][0])
    #     logger.warning(f"second parse: {converted_path=}")

    code = converted_path["code"][0]
    source = db_utils.LoginSource[str(converted_path["source"][0]).upper()]

    source_id_list = converted_path.get("source_id")  # ex: discord id
    source_id = source_id_list[0] if source_id_list else None

    source_name_list = converted_path.get("source_name")  # ex: discord username
    source_name = source_name_list[0] if source_name_list else None

    user_data = await get_github_user(code=code)
    logger.warning(user_data)

    follow_up_code = db_utils.login_or_create_renzen_user_with_github_oauth(
        github_email=user_data["email"],  # can be empty
        github_username=user_data["login"],
        login_source=source,
        source_id=source_id,
        source_name=source_name,
    )

    # silly hack
    path = converted_path["path"][0].replace("?dummy_hack=dummy_hack", "")

    # redirect
    # Annoying roundabout way to keep jwt out of URL by returning a one-time-use code for user

    if source == db_utils.LoginSource.VS_CODE:
        build_char = "&"
    else:
        build_char = "?"

    built_redirect_path = (
        path + build_char + parse.urlencode({"follow-up-code": follow_up_code.code})
    )
    logger.warning(f"{built_redirect_path}")
    raise web.HTTPFound(built_redirect_path)


async def github_oauth_jwt_followup(request: web.Request) -> web.Response:
    """Get jwt using one-time-code"""

    # use code to verify user and delete one-time-use code from db
    follow_up_code = request.url.query["follow-up-code"]
    renzen_user_info = db_utils.get_renzen_user_by_code(follow_up_code)
    # db_utils.invalidate_code(code=follow_up_code)

    logger.warning("AFTER INVALIDATING CODE")
    logger.warning(f"{renzen_user_info}")
    # logger.warning(f"{renzen_user_info.renzen_user_name}")
    logger.warning(f"{dataclasses.asdict(renzen_user_info)}")
    payload = dataclasses.asdict(renzen_user_info)
    payload.pop("creation_timestamp")

    encoded_jwt = jwt.encode(payload, secret_utils.JWT_SECRET, algorithm="HS256")  # type: ignore

    return web.Response(
        text=encoded_jwt,
    )


resource = cors.add(app.router.add_resource("/get_snippets"))
cors.add(resource.add_route("POST", vs_ext_get_snippets))

resource = cors.add(app.router.add_resource("/star"))
cors.add(resource.add_route("POST", vs_ext_star))

resource = cors.add(app.router.add_resource("/forward"))
cors.add(resource.add_route("POST", chrome_ext_forward))

resource = cors.add(app.router.add_resource("/"))
cors.add(resource.add_route("GET", privacy_policy_page))

resource = cors.add(app.router.add_resource("/api/auth/github"))
cors.add(resource.add_route("GET", github_oauth))

resource = cors.add(app.router.add_resource("/follow-up-code"))
cors.add(resource.add_route("POST", github_oauth_jwt_followup))

web.run_app(app, port=80, host="0.0.0.0")
