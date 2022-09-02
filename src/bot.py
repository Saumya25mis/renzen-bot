# pylint: disable=import-error
"""Discord Bot."""

import logging
import discord
from discord.ext import commands
import psycopg2

from src import get_secret

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

SECRETS = get_secret.get_secret()
TOKEN = SECRETS["eklie-token"]
GUILD = SECRETS["eklie-guild"]


DB_PASSWORD = SECRETS["postgres-password"]
DB_USERNAME = SECRETS["postgres-username"]
DB_PORT = SECRETS["postgres-port"]
DB_ENDPOINT = SECRETS["postgres-endpoint"]


conn = psycopg2.connect(
    database="postgres",
    user=DB_USERNAME,
    password=DB_PASSWORD,
    host=DB_ENDPOINT,
    port=DB_PORT,
    sslmode="require",
)

conn.autocommit = True

cur = conn.cursor()
# https://www.psycopg.org/docs/usage.html

# cur.execute()
# cur.fetchone()
# conn.commit()
# cur.close()
# conn.close
# conn.rollback()

intents = discord.Intents.all()
intents.message_content = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command()
async def test(ctx, arg):
    """Test command."""
    logger.debug("Received test command.")
    await ctx.send(arg)


@bot.event
async def on_message(message: discord.Message):
    """On message test."""
    logger.debug("Received on_message event")
    if message.author == bot.user:
        return
    await message.channel.send("ping!!!")

    # save to db
    logger.debug("Preparing to INSERT into DB")
    cur.execute(
        "INSERT INTO test (num, data) VALUES (%s, %s)", (message.id, message.content)
    )
    logger.debug("Executed INSERT")
    # conn.commit()
    # logger.debug("Committed to DB")

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


bot.run(TOKEN)
