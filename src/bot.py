# pylint:disable=import-error

"""Discord Bot."""

import logging
import discord
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
