# pylint: disable=import-error
"""Discord Bot."""

import logging
import asyncio
import discord
from discord.ext import commands

from flask import Flask
from celery import Celery

from src import secret_utils

app = Flask(__name__)
celery_app = Celery()
app.config["SECRET_KEY"] = "temp--secret--key"


@celery_app.task
async def run_flask_health_check():  # pylint: disable=unused-argument
    """Flask app for health check."""
    app.run(debug=True, port=80)


@app.route("/")
def health_check():
    """Return Hello World."""
    return "<h1>Health Check Success</h1>", 200


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

intents = discord.Intents.all()
intents.message_content = True
intents.guild_messages = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)


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


async def async_bot_run():
    """Try."""
    bot.run(secret_utils.TOKEN)


asyncio.run(async_bot_run())

# run_flask_health_check.apply_async()

app.run(debug=True, port=80, host="0.0.0.0")
