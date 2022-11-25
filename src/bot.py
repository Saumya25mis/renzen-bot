# pylint: disable=import-error, no-member
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

TEMP_ID = 273685734483820554
# sqs_client = boto3.client("sqs", region_name="us-west-1")
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
        # response = sqs_client.receive_message(
        #     QueueUrl=get_queue_url(),
        #     MaxNumberOfMessages=1,
        #     WaitTimeSeconds=10,
        # )

        # print(f"Number of messages received: {len(response.get('Messages', []))}")

        # temp_user = self.bot.get_user(TEMP_ID)

        # if temp_user is None:
        #     print(f"USER {TEMP_ID} NOT FOUND")
        #     return

        # print(f"{temp_user.name} was found!")

        for message in queue.receive_messages():

            message_json = json.loads(message.body)
            request_content = json.loads(message_json["request_content"])

            print(f"message_json: {str(message_json)}")
            user_id = db_utils.query_db_by_code(request_content["login-code"])
            print(f"{user_id=}")

            temp_user = self.bot.get_user(user_id)

            if temp_user is None:
                print(f"USER {user_id} NOT FOUND")
                return

            print(f"{temp_user.name} was found!")

            print(message.body)
            await temp_user.send(message.body)
            message.delete()

        # for message in response.get("Messages", []):
        #     message_body = message["Body"]
        #     print(f"Message body: {json.loads(message_body)}")
        #     print(f"Receipt Handle: {message['ReceiptHandle']}")
        #     # await temp_user.send({json.loads(message_body)})
        #     await temp_user.send(message_body)


@my_bot.command()
async def test(ctx, arg):
    """Test command. Prints what follows `!test`. ex: `!test hi`"""
    # logger.info("Received test command.")
    await ctx.send("Received test command.")
    await ctx.send(arg)


@my_bot.event
async def on_message(message: discord.Message):
    """On message test."""
    # logger.info("Received on_message event")
    if message.author == my_bot.user:
        return

    if message.content == "code":
        # create a code and associate it with the user id
        # this code can be used to subscribe in chrome extension
        await message.channel.send("code command ack")
        key = db_utils.create_code_key(message.author.id)
        await message.channel.send(f"Your key is: {key}")
        return

    # temp debug ack
    await message.channel.send("hazel is amazing!!!")

    # save to db
    # db_utils.save_message_to_db(message=message)

    # process commands
    await my_bot.process_commands(message)


# def get_queue_url():
#     """Get url."""
#     # sqs_client = boto3.client("sqs", region_name="us-west-2")
#     response = sqs_client.get_queue_url(
#         QueueName="MyQueue.fifo",
#     )
#     return response["QueueUrl"]


async def main_async():
    """Main."""
    await my_bot.add_cog(MyCog(my_bot))
    await my_bot.start(secret_utils.TOKEN)


asyncio.run(main_async())
