"""Expose endpoint for aiohttp server"""

import json
import logging
import uuid
from typing import Dict

import boto3
from aiohttp import web

from src.common import db_utils

logger = logging.getLogger(__name__)

sqs_client = boto3.client("sqs", region_name="us-west-1")


async def handle(request: web.Request) -> web.Response:
    """Health check response."""
    response_obj = {"status": "success"}
    return web.Response(text=json.dumps(response_obj))


async def forward(request: web.Request) -> web.Response:
    """forward check response."""

    logger.info("Received forward request.")

    request_id = str(uuid.uuid4())

    request_text = await request.text()

    send_message(message={"request_content": request_text})
    response_obj = {"status": f"success forward {request_id}"}
    return web.Response(text=json.dumps(response_obj))


async def check_valid_code(request: web.Request) -> web.Response:
    """Used by chrome extension to check if user can login with code."""

    logger.info("Received valid code request.")

    request_text = await request.text()
    result = db_utils.query_db_by_code(str(request_text))

    if result:
        return web.Response(text="valid")
    return web.Response(text="invalid")


def get_queue_url() -> str:
    """Get Queue Url."""
    response = sqs_client.get_queue_url(
        QueueName="MyQueue.fifo",
    )
    return str(response["QueueUrl"])


def send_message(message: Dict[str, str]) -> None:
    """Send message to queue."""
    logger.info("Adding message to queue.")
    response = sqs_client.send_message(
        QueueUrl=get_queue_url(),
        MessageBody=json.dumps(message),
        MessageGroupId="MyTestId",
    )


app = web.Application()
app.router.add_get("/", handle)
app.router.add_get("/forward", forward)
app.router.add_route("POST", "/forward", forward)
app.router.add_route("GET", "/valid_code", check_valid_code)

web.run_app(app, port=80, host="0.0.0.0")
