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


class MyClient(discord.Client):
    """Client class."""

    async def on_ready(self):
        """On Ready."""
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message):
        """On Message."""
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith("!hello"):
            await message.reply("Hello!", mention_author=True)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)


bot = commands.Bot(command_prefix="?", intents=intents)


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


bot.run(TOKEN)
