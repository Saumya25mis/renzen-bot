# pylint: disable=import-error, no-member, unused-argument, unused-variable, too-many-locals
"""Discord Bot."""

import asyncio
import discord

from src import secret_utils
from src import db_utils

from bot_constants import my_bot
from bot_utils import format_search_embed
from batch_update_cog import MyCog


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
async def today(interaction: discord.Interaction):
    """Words to color or highlight in snippets."""

    await interaction.response.send_message("Gathering snippets for today...")

    snippet_matches = db_utils.query_db_by_date()
    await format_search_embed(interaction, snippet_matches, title="Today's Snippets")


@my_bot.tree.command()
async def search(
    interaction: discord.Interaction,
    search_for: str,
):
    """Searches saved urls and content"""

    await interaction.response.send_message("Searching...")

    snippet_matches = db_utils.search_snippets_by_str(search_for, interaction.user.id)
    url_matches = db_utils.search_urls_by_str(search_for, interaction.user.id)
    match_ids = await format_search_embed(
        interaction, snippet_matches, search_for=search_for, title="Matching Snippets"
    )
    await format_search_embed(
        interaction, url_matches, match_ids, title="Matching URLS"
    )


@my_bot.event
async def on_ready():
    """Sync slash tree"""
    print("New bot deployed!")
    await my_bot.tree.sync()
    print("Commands Synced!!")

    # get notification user
    user: discord.User = await my_bot.fetch_user(273685734483820554)

    await user.send("New Bot Deploy!")


@my_bot.event
# async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Processes reactions."""

    user: discord.User = await my_bot.fetch_user(payload.user_id)
    message: discord.Message = await user.fetch_message(payload.message_id)

    print("Reaction ack")
    # await user.send("Reaction ack")

    emoji = str(payload.emoji)

    # delete post on thumbs down
    if emoji == "👎":
        await message.delete()
        print(f"Deleted message: {message.content}")

    # print(locals())


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
