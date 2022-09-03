# pylint: disable=import-error
"""Discord Bot."""

import logging
import discord
from discord.ext import commands

from src import secret_utils
from src import db_utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

intents = discord.Intents.all()
intents.message_content = True
intents.guild_messages = True

bot_activity = discord.Activity(
    state="being developed at https://github.com/renadvent/eklie"
)

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    activity=bot_activity,
)


@bot.command()
async def test(ctx, arg):
    """Test command."""
    logger.info("Received test command.")
    await ctx.send(arg)


@bot.event
async def on_message(message: discord.Message):
    """On message test."""
    logger.info("Received on_message event")
    if message.author == bot.user:
        return

    # temp debug ack
    await message.channel.send("ping!!!")

    # save to db
    db_utils.save_message_to_db(message=message)

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


bot.run(secret_utils.TOKEN)
