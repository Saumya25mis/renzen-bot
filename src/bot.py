# pylint: disable=import-error, no-member, unused-argument
"""Discord Bot."""

import json
import asyncio
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
    """Slash command to get chrome extension code."""
    await interaction.response.send_message("code command ack")
    key = db_utils.create_code(interaction.user.id, interaction.user.display_name)
    await interaction.response.send_message(f"Your key is: {key}")
    return


@my_bot.tree.command()
async def invalidate_codes(interaction: discord.Interaction):
    """Test command. Prints what follows `!test`. ex: `!test hi`"""
    await interaction.response.send_messaged("invalidate_codes command ack")
    db_utils.invalidate_codes(interaction.user.id)
    await interaction.response.send_message("All codes have been invalidated")
    return


@my_bot.tree.command()
async def search(interaction: discord.Interaction, arg):
    """Test command. Prints what follows `!test`. ex: `!test hi`"""
    await interaction.response.send_message("search command ack")
    await interaction.response.send_message(f"{arg=}")
    snippet_matches = db_utils.search_snippets_by_str(arg, interaction.user.id)
    url_matches = db_utils.search_urls_by_str(arg, interaction.user.id)
    await interaction.response.send_message(f"{snippet_matches=}")
    await interaction.response.send_message(f"{url_matches=}")
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

                temp_user = self.bot.get_user(user_id)

                if temp_user is None:
                    print(f"USER {user_id} NOT FOUND")
                    continue

                print(f"{temp_user.name} was found!")

                print(message.body)
                await send_formatted_discord_message(temp_user, request_content)
                # await temp_user.send(message.body)
                message.delete()

            except Exception as e:  # pylint:disable=broad-except, invalid-name
                print(f"Could not deliver message. Will not retry {e}")
                print(f"{message.body=}")
                message.delete()


async def send_formatted_discord_message(temp_user, request_content):
    """Sends message formatted."""
    await temp_user.send(f"{request_content['snippet']} \n {request_content['URL']}")


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
