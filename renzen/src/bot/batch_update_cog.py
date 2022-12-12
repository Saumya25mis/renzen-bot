"""Queue cog."""

import json
import logging
from typing import Optional

import discord
from discord.ext import commands, tasks
from src.common import queue_utils
from src.bot import bot_utils
from src.common import db_utils

logger = logging.getLogger(__name__)


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

        message_type, messages = queue_utils.receive_messages()

        for message in messages:

            temp_user: Optional[discord.User] = None

            try:

                if message_type == "aws":
                    message_json = json.loads(message.body)
                    request_content = json.loads(message_json["request_content"])
                elif message_type == "rabbit":
                    if not message:
                        continue
                    message_json = json.loads(message)
                    request_content = json.loads(message_json["request_content"])
                else:
                    # do nothing
                    return

                login_user_relation: Optional[
                    db_utils.LoginCodes
                ] = db_utils.query_db_by_code(request_content["login-code"])

                if not login_user_relation:
                    message.delete()
                    continue

                temp_user = self.bot.get_user(int(login_user_relation.discord_user_id))

                if temp_user is None:
                    message.delete()
                    continue

                embed = await bot_utils.send_formatted_discord_message(
                    request_content=request_content,
                    user_id=login_user_relation.discord_user_id,
                )

                await temp_user.send(embed=embed)

            except Exception as e:  # pylint:disable=broad-except, invalid-name
                logger.info("Could not deliver message. Will not retry\n %s", e)
                logger.info(message)
                if temp_user:
                    await temp_user.send(
                        f"Could not deliver message. Will not retry\n{e}"
                    )

            if message_type == "aws":
                message.delete()
