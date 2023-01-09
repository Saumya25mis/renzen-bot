"""Discord Bot."""

import asyncio
import logging
import os

import discord
from discord.ext import commands
from src.bot.batch_update_cog import BatchForwardSnippets
from src.common import db_utils, secret_utils

logger = logging.getLogger(__name__)


discord.utils.setup_logging()

intents = discord.Intents.all()
intents.message_content = True
intents.guild_messages = True
intents.members = True

my_bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)

NOTIFICATION_USER = 273685734483820554
PRODUCTION_ALERTS_CHANNEL = 1050487198882992268
STAGING_ALERTS_CHANNEL = 1050487229631451238


@my_bot.tree.command()
async def get_code(interaction: discord.Interaction) -> None:
    """Creates code used to sign into chrome extension to save content to discord."""
    logger.info("Command Detected: get_code")
    login_code = db_utils.create_code_for_discord_user(
        interaction.user.id, interaction.user.display_name
    )
    await interaction.response.send_message(f"Your key is: {login_code.code}")
    return


@my_bot.event
async def on_ready() -> None:
    """Sync slash tree"""
    logger.info("New bot deployed!")
    await my_bot.tree.sync()

    # send to notification user
    user: discord.User = await my_bot.fetch_user(NOTIFICATION_USER)

    await user.send("New Bot Deploy!")

    if os.getenv("CURRENT_ENVIRONMENT") == "staging":
        channel = my_bot.get_channel(STAGING_ALERTS_CHANNEL)
        if channel:
            await channel.send(content="New Staging Bot Deploy!")  # type: ignore
    elif os.getenv("CURRENT_ENVIRONMENT") == "production":
        channel = my_bot.get_channel(PRODUCTION_ALERTS_CHANNEL)
        if channel:
            await channel.send(content="New Staging Bot Deploy!")  # type: ignore


async def main_async() -> None:
    """Main."""
    await my_bot.add_cog(BatchForwardSnippets(my_bot))
    await my_bot.start(secret_utils.TOKEN)  # type: ignore


asyncio.run(main_async())


# @my_bot.event
# async def on_message(message: discord.Message) -> None:
#     """On message test."""
#     if message.author == my_bot.user:
#         return

#     logger.info("Event Detected: on_message")

#     await my_bot.process_commands(message)


# @my_bot.tree.command()
# async def invalidate_codes(interaction: discord.Interaction) -> None:
#     """Invalidates previously created codes."""
#     logger.info("Command Detected: invalidate_codes")
#     db_utils.invalidate_codes(interaction.user.id)
#     await interaction.response.send_message("All codes have been invalidated")
#     return


# @my_bot.tree.command()
# async def erase_sinppets(interaction: discord.Interaction) -> None:
#     """Erases saved content from database (will not be able to search past content)."""
#     logger.info("Command Detected: erase_sinppets")
#     await interaction.response.send_message("Not yet implemented.")


# @my_bot.tree.command()
# async def today(interaction: discord.Interaction) -> None:
#     """Returns a summary of snippets saved today."""
#     logger.info("Command Detected: today")
#     await interaction.response.send_message("Gathering snippets for today...")

#     snippet_matches = db_utils.query_db_by_date()
#     found_message_ids, embeds = await format_search_embed(
#         snippet_matches=snippet_matches, title="Today's Snippets"
#     )

#     for embed in embeds:
#         await interaction.followup.send(embed=embed)


# @my_bot.tree.command()
# async def search_snippets(
#     interaction: discord.Interaction,
#     search_for: str,
# ) -> None:
#     """Searches saved urls and content"""
#     logger.info("Command Detected: search")

#     await interaction.response.send_message(f"Searching for {search_for}...")

#     snippet_matches = db_utils.search_snippets_by_str(search_for, interaction.user.id)
#     _, embeds = await format_search_embed(
#         snippet_matches=snippet_matches,
#         search_for=search_for,
#         title="Matching Snippet Content",
#         description=f"Search Results for {search_for}",
#     )

#     for embed in embeds:
#         await interaction.followup.send(embed=embed)


# @my_bot.tree.command()
# async def search_urls(
#     interaction: discord.Interaction,
#     search_for: str,
# ) -> None:
#     """Searches saved urls and content"""
#     logger.info("Command Detected: search")

#     await interaction.response.send_message(f"Searching for {search_for}...")

#     url_matches = db_utils.search_urls_by_str(search_for, interaction.user.id)

#     _, embeds = await format_search_embed(
#         snippet_matches=url_matches,
#         search_for=search_for,
#         title="Matching URLS Only",
#         description=f"Search Results for {search_for}",
#     )

#     for embed in embeds:
#         await interaction.followup.send(embed=embed)


# @my_bot.event
# async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
#     """Processes reactions."""
#     logger.info("Event Detected: on_raw_reaction_add")
#     user: discord.User = await my_bot.fetch_user(payload.user_id)
#     message: discord.Message = await user.fetch_message(payload.message_id)

#     emoji = str(payload.emoji)

#     # delete post on thumbs down
#     if emoji == "👎":
#         await message.delete()
