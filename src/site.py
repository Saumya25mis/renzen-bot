# pylint: disable=import-error
"""Expose endpoint for aiohttp server"""

import json
import uuid
import boto3
from aiohttp import web


sqs_client = boto3.client("sqs", region_name="us-west-1")


async def handle(request):  # pylint:disable=unused-argument
    """Health check response."""
    response_obj = {"status": "success"}
    return web.Response(text=json.dumps(response_obj))


async def forward(request):  # pylint:disable=unused-argument
    """forward check response."""
    request_id = str(uuid.uuid4())

    print(f"Received request to forward: {request_id}")

    request_text = await request.text()
    print(f"{request_text=}")

    send_message(message={"request_content": request_text})
    response_obj = {"status": f"success forward {request_id}"}
    return web.Response(text=json.dumps(response_obj))


def get_queue_url():
    """Get Queue Url."""
    response = sqs_client.get_queue_url(
        QueueName="MyQueue.fifo",
    )
    return response["QueueUrl"]


def send_message(message):
    """Send message to queue."""
    response = sqs_client.send_message(
        QueueUrl=get_queue_url(),
        MessageBody=json.dumps(message),
        MessageGroupId="MyTestId",
    )
    print(f"{response=}")


app = web.Application()
app.router.add_get("/", handle)
app.router.add_get("/forward", forward)
app.router.add_route("POST", "/forward", forward)

web.run_app(app, port=80, host="0.0.0.0")
