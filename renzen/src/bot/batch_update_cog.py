"""Queue cog."""

import json
import logging
from typing import Optional

import discord
from discord.ext import commands, tasks
from src.bot import bot_utils
from src.common import db_utils, queue_utils

logger = logging.getLogger(__name__)


class CogException(Exception):
    """Bot Cog Exception."""

    def __init__(self) -> None:
        super()


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
                if not message:
                    continue

                if message_type == "aws":
                    message_json = json.loads(message.body)
                else:
                    message_json = json.loads(message)

                db_id = json.loads(message_json["request_content"])

                snippet = db_utils.load_snippet_from_db(db_id)
                if snippet:
                    discord_user_info = db_utils.get_discord_user_by_renzen_user_id(
                        snippet.renzen_user_id
                    )
                    if discord_user_info:
                        temp_user = self.bot.get_user(
                            int(discord_user_info.discord_user_id)
                        )
                    else:
                        raise CogException
                else:
                    continue

                if temp_user is None:
                    message.delete()
                    continue

                embed = await bot_utils.send_formatted_discord_message(snippet=snippet)

                await temp_user.send(embed=embed)

            except (  # pylint:disable=broad-except, invalid-name
                Exception,
                CogException,
            ) as e:
                logger.exception("Could not deliver message. Will not retry")
                logger.info(message)
                if temp_user:
                    await temp_user.send(
                        f"Could not deliver message. Will not retry\n{e}"
                    )

            if message_type == "aws":
                message.delete()
