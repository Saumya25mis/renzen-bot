"""Queue cog."""

import json
import boto3
from discord.ext import commands, tasks
from src import bot_utils
from src import db_utils

sqs = boto3.resource("sqs", region_name="us-west-1")
queue = sqs.get_queue_by_name(QueueName="MyQueue.fifo")


class BatchForwardSnippets(commands.Cog):
    """Cog to run sqs updates."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.batch_update.start()

    async def cog_unload(self) -> None:
        """Unload cog."""
        self.batch_update.cancel()

    @tasks.loop(seconds=2)
    async def batch_update(self) -> None:
        """Receive message."""

        for message in queue.receive_messages():

            try:

                message_json = json.loads(message.body)
                request_content = json.loads(message_json["request_content"])

                print(f"message_json: {str(message_json)}")
                user = db_utils.query_db_by_code(request_content["login-code"])
                print(f"{user=}")

                if not user:
                    print("NO USER FOUND TO MATCH CODE")
                    message.delete()
                    continue

                temp_user = self.bot.get_user(int(user.discord_user_id))

                if temp_user is None:
                    print(f"USER {user.discord_user_id} NOT FOUND")
                    message.delete()
                    continue

                print(f"{temp_user.name} was found!")

                print(message.body)
                await bot_utils.send_formatted_discord_message(
                    temp_user, request_content, user.discord_user_id
                )

            except Exception as e:  # pylint:disable=broad-except, invalid-name
                print(f"Could not deliver message. Will not retry\n{e}")
                print(f"{message.body=}")
                if temp_user:
                    await temp_user.send(
                        f"Could not deliver message. Will not retry\n{e}"
                    )

            message.delete()
