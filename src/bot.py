# pylint:disable=import-error

"""Discord Bot."""

import logging
import discord
from src import get_secret

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

SECRETS = get_secret.get_secret()
TOKEN = SECRETS["eklie-token"]
GUILD = SECRETS["eklie-guild"]

intents = discord.Intents.default()
client = discord.Client(intents=intents)

logging.info("got client")


@client.event
async def on_ready():
    """On Ready event."""
    logging.info("We have logged in as %s", client)


@client.event
async def on_message(message):
    """On message event."""
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


client.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
