# pylint: disable=invalid-name
"""Queue utils."""
import json
import logging
import os
from typing import Any, Dict, Tuple

import boto3
import pika  # type: ignore

logger = logging.getLogger(__name__)
CURRENT_ENVIRONMENT = os.getenv("CURRENT_ENVIRONMENT")

queue_name = "TESTQUEUE"  # f"{CURRENT_ENVIRONMENT}-MyQueue.fifo"
aws_queue = None


if not os.getenv("RUN_LOCAL"):
    # set up access to aws queue
    sqs = boto3.resource("sqs", region_name="us-west-1")
    aws_queue = sqs.get_queue_by_name(QueueName=f"{CURRENT_ENVIRONMENT}-MyQueue.fifo")
else:
    # set up access to rabbit queue
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq", port=5672, heartbeat=0)
    )
    rabbit_channel = connection.channel()
    rabbit_queue = rabbit_channel.queue_declare(queue=queue_name)


def receive_messages() -> Tuple[str, Any]:
    """Receive messages from queues."""

    if os.getenv("RUN_LOCAL"):
        if rabbit_queue:
            method_frame, header_frame, body = rabbit_channel.basic_get(
                queue_name, auto_ack=True
            )

            if body:
                print(f"{method_frame=}")
                print(f"{header_frame=}")
                print(f"{body=}")
                body_str = str(body, "UTF-8")
                print(f"{body_str=}")
                return ("rabbit", [body_str])
            return ("rabbit", [body])
    else:
        if aws_queue:
            return ("aws", aws_queue.receive_messages())
    return ("", None)


def send_message(message: Dict[str, str]) -> None:
    """Send message to queue."""
    logger.info("Adding message to queue.")

    message_body = json.dumps(message)
    queue_id = "MyTestId"

    if os.getenv("RUN_LOCAL"):
        if rabbit_queue:
            rabbit_channel.basic_publish(
                exchange="", routing_key=queue_name, body=message_body
            )
            # print(f" [x] Sent {message_body=}'")
    else:
        if aws_queue:
            response = aws_queue.send_message(
                MessageBody=message_body,
                MessageGroupId=queue_id,
            )
