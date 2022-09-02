# pylint:disable=import-error

"""Discord Bot."""

import logging
import discord
from discord.ext import commands

from src import get_secret

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

SECRETS = get_secret.get_secret()
TOKEN = SECRETS["eklie-token"]
GUILD = SECRETS["eklie-guild"]

intents = discord.Intents.all()
intents.message_content = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command()
async def test(ctx, arg):
    """Test command."""
    await ctx.send(arg)


@bot.event()
async def _on_message(message):
    """On message test."""
    await message.channel.sent("ping!!!")


@bot.event()
async def _on_message(ctx, message):
    """On message test."""
    await ctx.send(f"pong ctx {message}!!!")


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


bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
