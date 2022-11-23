# pylint: disable=import-error
"""Discord Bot."""

import logging

import asyncio
import json
import boto3
import discord


# from aiohttp import web
from discord.ext import commands

from src import secret_utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

intents = discord.Intents.all()
intents.message_content = True
intents.guild_messages = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)

TEMP_ID = 273685734483820554
sqs_client = boto3.client("sqs", region_name="us-west-1")


@bot.command()
async def test(ctx, arg):
    """Test command. Prints what follows `!test`. ex: `!test hi`"""
    logger.info("Received test command.")
    await ctx.sent("Received test command.")
    await ctx.send(arg)


@bot.event
async def on_message(message: discord.Message):
    """On message test."""
    logger.info("Received on_message event")
    if message.author == bot.user:
        return

    # temp debug ack
    await message.channel.send("hazel is amazing!!!")

    # save to db
    # db_utils.save_message_to_db(message=message)

    # process commands
    await bot.process_commands(message)


@bot.group()
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send(f"No, {ctx.subcommand_passed} is not cool")


@cool.command(name="bot")
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send("Yes, the bot is cool.")


def get_queue_url():
    """Get url."""
    # sqs_client = boto3.client("sqs", region_name="us-west-2")
    response = sqs_client.get_queue_url(
        QueueName="MyQueue.fifo",
    )
    return response["QueueUrl"]


async def receive_message():
    """Receive message."""
    response = sqs_client.receive_message(
        QueueUrl=get_queue_url(),
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )

    print(f"Number of messages received: {len(response.get('Messages', []))}")

    temp_user = bot.get_user(TEMP_ID)

    for message in response.get("Messages", []):
        message_body = message["Body"]
        print(f"Message body: {json.loads(message_body)}")
        print(f"Receipt Handle: {message['ReceiptHandle']}")
        await temp_user.send({json.loads(message_body)})


async def poll():
    """Runs  async port."""
    while True:
        await asyncio.sleep(1)
        await receive_message()

    # runner = web.AppRunner(app)
    # await runner.setup()
    # site = web.TCPSite(runner, 'localhost', 80)
    # await site.start()


loop = asyncio.get_event_loop()
loop.run_until_complete(poll())


# async def forward(request):
#     """Forwards request to bot."""
#     pass

# app = web.Application()
# app.add_routes([web.get("/forward", forward)])

# async def runner():
#     """Runs  async port."""
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, 'localhost', 80)
#     await site.start()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(runner())

bot.run(secret_utils.TOKEN)
