"""Discord Bot."""

import asyncio
import discord
from discord.ext import commands

from src import secret_utils
from src import db_utils

from src.bot_utils import format_search_embed
from src.batch_update_cog import BatchForwardSnippets

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


@my_bot.tree.command()
async def get_code(interaction: discord.Interaction) -> None:
    """Creates code used to sign into chrome extension to save content to discord."""
    key = db_utils.create_code(interaction.user.id, interaction.user.display_name)
    await interaction.response.send_message(f"Your key is: {key}")
    return


@my_bot.tree.command()
async def invalidate_codes(interaction: discord.Interaction) -> None:
    """Invalidates previously created codes."""
    db_utils.invalidate_codes(interaction.user.id)
    await interaction.response.send_message("All codes have been invalidated")
    return


@my_bot.tree.command()
async def erase_sinppets(interaction: discord.Interaction) -> None:
    """Erases saved content from database (will not be able to search past content)."""
    await interaction.response.send_message("Not yet implemented.")


@my_bot.tree.command()
async def today(interaction: discord.Interaction) -> None:
    """Returns a summary of snippets saved today."""

    await interaction.response.send_message("Gathering snippets for today...")

    snippet_matches = db_utils.query_db_by_date()
    await format_search_embed(interaction, snippet_matches, title="Today's Snippets")


@my_bot.tree.command()
async def search(
    interaction: discord.Interaction,
    search_for: str,
) -> None:
    """Searches saved urls and content"""

    await interaction.response.send_message("Searching...")

    snippet_matches = db_utils.search_snippets_by_str(search_for, interaction.user.id)
    url_matches = db_utils.search_urls_by_str(search_for, interaction.user.id)
    match_ids = await format_search_embed(
        interaction,
        snippet_matches,
        search_for=search_for,
        title="Matching Snippet Content",
        description=f"Search Results for {search_for}",
    )
    await format_search_embed(
        interaction,
        url_matches,
        search_for=search_for,
        exclude_message_ids=match_ids,
        title="Matching URLS Only",
        description=f"Search Results for {search_for}",
    )


@my_bot.event
async def on_ready() -> None:
    """Sync slash tree"""
    print("New bot deployed!")
    await my_bot.tree.sync()
    print("Commands Synced!!")

    # send to notification user
    user: discord.User = await my_bot.fetch_user(NOTIFICATION_USER)

    await user.send("New Bot Deploy!")


@my_bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
    """Processes reactions."""

    user: discord.User = await my_bot.fetch_user(payload.user_id)
    message: discord.Message = await user.fetch_message(payload.message_id)

    print("Reaction ack")

    emoji = str(payload.emoji)

    # delete post on thumbs down
    if emoji == "👎":
        await message.delete()
        print(f"Deleted message: {message.content}")


@my_bot.event
async def on_message(message: discord.Message) -> None:
    """On message test."""
    if message.author == my_bot.user:
        return

    await my_bot.process_commands(message)


async def main_async() -> None:
    """Main."""
    await my_bot.add_cog(BatchForwardSnippets(my_bot))
    await my_bot.start(secret_utils.TOKEN)


asyncio.run(main_async())
