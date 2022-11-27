# pylint: disable=import-error, no-member, unused-argument
"""Discord Bot."""

import json
import asyncio
from urllib.parse import urlparse
import boto3
import discord

# from discord import app_commands


from discord.ext import commands, tasks

from src import secret_utils
from src import db_utils

discord.utils.setup_logging()

intents = discord.Intents.all()
intents.message_content = True
intents.guild_messages = True

my_bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)

sqs = boto3.resource("sqs", region_name="us-west-1")
queue = sqs.get_queue_by_name(QueueName="MyQueue.fifo")


@my_bot.tree.command()
async def get_code(interaction: discord.Interaction):
    """Creates code used to sign into chrome extension to save content to discord."""
    key = db_utils.create_code(interaction.user.id, interaction.user.display_name)
    await interaction.response.send_message(f"Your key is: {key}")
    return


@my_bot.tree.command()
async def invalidate_codes(interaction: discord.Interaction):
    """Invalidates previously created codes."""
    db_utils.invalidate_codes(interaction.user.id)
    await interaction.response.send_message("All codes have been invalidated")
    return


@my_bot.tree.command()
async def erase_sinppets(interaction: discord.Interaction):
    """Erases saved content from database (will not be able to search past content)."""
    await interaction.response.send_message("Not yet implemented.")


@my_bot.tree.command()
async def search(
    interaction: discord.Interaction,
    search_for: str,
):
    """Searches saved urls and content"""

    snippet_matches = db_utils.search_snippets_by_str(search_for, interaction.user.id)
    url_matches = db_utils.search_urls_by_str(search_for, interaction.user.id)

    embed = discord.Embed(
        title="Search Results",
        description=f"Results for '{search_for}'",
        colour=discord.Colour.random(),
    )
    embed.set_author(name="renzen")

    for snippet in snippet_matches:
        embed.add_field(name=snippet[1], value=snippet[2])

    for snippet in url_matches:
        embed.add_field(name=snippet[1], value=snippet[2])

    await interaction.response.send_message(embed=embed)

    return


@my_bot.event
async def on_ready():
    """Sync slash tree"""
    await my_bot.tree.sync()
    print("Commands Synced!!")


class MyCog(commands.Cog):
    """Cog to run sqs updates."""

    def __init__(self, bot):
        self.bot = bot
        self.batch_update.start()

    async def cog_unload(self):
        """Unload cog."""
        self.batch_update.cancel()

    @tasks.loop(seconds=2)
    async def batch_update(self):
        """Receive message."""

        for message in queue.receive_messages():

            try:

                message_json = json.loads(message.body)
                request_content = json.loads(message_json["request_content"])

                print(f"message_json: {str(message_json)}")
                user_id = db_utils.query_db_by_code(request_content["login-code"])
                print(f"{user_id=}")

                if not user_id:
                    print("NO USER FOUND TO MATCH CODE")
                    message.delete()
                    continue

                temp_user = self.bot.get_user(user_id)

                if temp_user is None:
                    print(f"USER {user_id} NOT FOUND")
                    message.delete()
                    continue

                print(f"{temp_user.name} was found!")

                print(message.body)
                await send_formatted_discord_message(
                    temp_user, request_content, user_id
                )
                # await temp_user.send(message.body)
                # message.delete()

            except Exception as e:  # pylint:disable=broad-except, invalid-name
                print(f"Could not deliver message. Will not retry\n{e}")
                print(f"{message.body=}")

            message.delete()


async def send_formatted_discord_message(temp_user, request_content, user_id):
    """Sends message formatted."""

    snippet = request_content["snippet"]
    url = request_content["URL"]
    parsed_url = urlparse(url=url)

    embed = discord.Embed(
        # title=url,
        colour=discord.Colour.random(),
    )

    # embed.set_author(name="renzen")
    embed.add_field(name=snippet, value=url)
    embed.set_thumbnail(url=f"{parsed_url}/favicon.ico")

    await temp_user.send(embed=embed)
    db_utils.save_snippet_to_db(url, snippet, user_id)


@my_bot.event
async def on_message(message: discord.Message):
    """On message test."""
    if message.author == my_bot.user:
        return

    # temp debug ack
    await message.channel.send("on_message ack")

    # process commands
    await my_bot.process_commands(message)


async def main_async():
    """Main."""
    await my_bot.add_cog(MyCog(my_bot))
    await my_bot.start(secret_utils.TOKEN)


asyncio.run(main_async())
