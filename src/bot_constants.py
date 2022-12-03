# pylint: disable=import-error, no-member, unused-argument, unused-variable, too-many-locals
"""Bot Constants."""

import boto3
import discord

from discord.ext import commands

discord.utils.setup_logging()

intents = discord.Intents.all()
intents.message_content = True
intents.guild_messages = True
intents.members = True

my_bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)

sqs = boto3.resource("sqs", region_name="us-west-1")
queue = sqs.get_queue_by_name(QueueName="MyQueue.fifo")

# ECS_CONTAINER_METADATA_URI_V4 = os.environ.get("ECS_CONTAINER_METADATA_URI_V4")


# def get_container_metadata():
#     res = requests.get(f"{ECS_CONTAINER_METADATA_URI_V4}/task").json()
