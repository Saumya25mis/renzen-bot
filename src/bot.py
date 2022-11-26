# pylint: disable=import-error, no-member, unused-argument
"""Discord Bot."""

import json
import asyncio
import boto3
import discord


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


@my_bot.command()
async def code(ctx, arg):
    """Test command. Prints what follows `!test`. ex: `!test hi`"""
    await ctx.channel.send("code command ack")
    key = db_utils.create_code_key(ctx.author.id, ctx.author.display_name)
    await ctx.channel.send(f"Your key is: {key}")
    return


@my_bot.command()
async def invalidate_codes(ctx, arg):
    """Test command. Prints what follows `!test`. ex: `!test hi`"""
    await ctx.channel.send("invalidate_codes command ack")
    db_utils.invalidate_codes(ctx.author.id)
    await ctx.channel.send("All codes have been invalidated")
    return


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
