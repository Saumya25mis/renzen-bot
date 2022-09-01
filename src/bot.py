# pylint:disable=import-error

"""Discord Bot."""

import random
import discord
from src import get_secret


SECRETS = get_secret.get_secret()
TOKEN = SECRETS["eklie-token"]
GUILD = SECRETS["eklie-guild"]

client = discord.Client()


@client.event
async def on_ready():
    """On Ready client action."""
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f"{client.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id})"
    )


@client.event
async def on_message(message):
    """On Message client action."""
    if message.author == client.user:
        return

    brooklyn_99_quotes = [
        "I'm the human form of the 💯 emoji.",
        "Bingpot!",
        (
            "Cool. Cool cool cool cool cool cool cool, "
            "no doubt no doubt no doubt no doubt."
        ),
    ]

    if message.content == "99!":
        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)


client.run(TOKEN)
