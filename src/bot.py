# pylint: disable=import-error, no-member, unused-argument, unused-variable
"""Discord Bot."""

import json
import asyncio
from urllib.parse import urlparse
import boto3
import discord

# import os

# import requests

# from discord import app_commands


from discord.ext import commands, tasks

from src import secret_utils
from src import db_utils

discord.utils.setup_logging()

intents = discord.Intents.all()
intents.message_content = True
intents.guild_messages = True
intents.members = True

my_bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)

sqs = boto3.resource("sqs", region_name="us-west-1")
queue = sqs.get_queue_by_name(QueueName="MyQueue.fifo")

# ECS_CONTAINER_METADATA_URI_V4 = os.environ.get("ECS_CONTAINER_METADATA_URI_V4")


# def get_container_metadata():
#     res = requests.get(f"{ECS_CONTAINER_METADATA_URI_V4}/task").json()


def trim_string(string, max_chars=1000):
    """Trims string."""
    return string[0 : min(len(string), max_chars)]


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
async def color_words(interaction: discord.Interaction):
    """Words to color or highlight in snippets."""
    await interaction.response.send_message("Not yet implemented.")


FULL_MAX_SIZE = 5000


@my_bot.tree.command()
async def today(interaction: discord.Interaction):
    """Words to color or highlight in snippets."""

    snippet_matches = db_utils.query_db_by_date()

    print(f"{snippet_matches=}")

    size = 6  # length of bot name
    embeds = []  # all embeds to send
    embed = None

    await interaction.response.send_message("Gathering snippets for today...")

    for snippet in snippet_matches:
        url = snippet[1]
        original_value = snippet[2]

        # get sized correctly

        # do initail trim
        trimmed_string = trim_string(original_value)
        escaped_string = discord.utils.escape_markdown(trimmed_string)

        if len(escaped_string) > 1000:
            # re-trim string
            value = discord.utils.escape_markdown(
                trim_string(trimmed_string, 1000 - (len(escaped_string - 1000)))
            )
            print(f"length of str: {value=}")
        else:
            value = escaped_string

        if not value:
            print("CLEANED SNIPPET HAS NO VALUE")
            print(f"Original: {snippet[2]=}")
            print(f"Final: {value=}")
            continue
        print(f"cleaned = {value=}")

        new_size = size + len(url) + len(value)

        if not embed or new_size >= FULL_MAX_SIZE:
            # create new embed
            embed = discord.Embed(
                title="Snippet Summary",
                description="Snippets saved today",
                colour=discord.Colour.random(),
            )
            embeds.append(embed)
            embed.set_author(name="renzen")
            size = 6

        size += len(url) + len(snippet[2])
        embed.add_field(name=url, value=value)

    for embed in embeds:
        await interaction.followup.send(embed=embed)

    await interaction.followup.send(embed=embed)


def bold_substring(value: str, substring: str):
    """Bolds substring while keeping case."""

    # get indexes for occurrences case-insensitive
    l_value = value.lower()
    l_substring = substring.lower()
    res = [i for i in range(len(l_value)) if l_value.startswith(l_substring, i)]

    sub_length = len(substring)
    bolded_list = list(value)

    bold = "**"

    # use indexes to insert bold markers and keep case
    offset_index = 0
    for index in res:
        bolded_list.insert(index + offset_index, bold)
        bolded_list.insert(index + offset_index + sub_length + 1, bold)
        offset_index += 2  # we are adding to indexes each loop

    bolded_string = "".join(bolded_list)

    # debug
    print(locals())

    return bolded_string


@my_bot.tree.command()
async def search(
    interaction: discord.Interaction,
    search_for: str,
):
    """Searches saved urls and content"""

    print(f"{search_for=}")

    snippet_matches = db_utils.search_snippets_by_str(search_for, interaction.user.id)
    url_matches = db_utils.search_urls_by_str(search_for, interaction.user.id)

    print(snippet_matches)

    embed = discord.Embed(
        title="Search Results",
        description=f"Results for '{search_for}'",
        colour=discord.Colour.random(),
    )
    embed.set_author(name="renzen")

    snippets_found = []

    for snippet in snippet_matches:
        snippets_found.append(snippet[0])
        cleaned_text = discord.utils.escape_markdown(snippet[2])
        value = bold_substring(trim_string(cleaned_text), search_for)
        if not value:
            print("CLEANED SNIPPET HAS NO VALUE")
            print(f"Original: {snippet[2]=}")
            print(f"Final: {value=}")
            continue
        print(f"cleaned and bolded text = {value=}")
        title = f"**{snippet[3]}**\n\n"
        embed.add_field(name=snippet[1], value=title + value)

    for snippet in url_matches:
        if not snippet[0] in snippets_found:
            cleaned_text = discord.utils.escape_markdown(snippet[2])
            value = trim_string(cleaned_text)
            if not value:
                print("CLEANED SNIPPET HAS NO VALUE")
                print(f"Original: {snippet[2]=}")
                print(f"Final: {value=}")
                continue
            print(f"cleanedtext = {value=}")
            title = f"**{snippet[3]}** \n\n"
            embed.add_field(name=snippet[1], value=title + value)

    await interaction.response.send_message(embed=embed)


@my_bot.event
async def on_ready():
    """Sync slash tree"""
    await my_bot.tree.sync()
    print("Commands Synced!!")

    # get notification user
    user: discord.User = await my_bot.fetch_user(273685734483820554)

    await user.send("New Bot Deploy!")


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

            except Exception as e:  # pylint:disable=broad-except, invalid-name
                print(f"Could not deliver message. Will not retry\n{e}")
                print(f"{message.body=}")

            message.delete()


async def send_formatted_discord_message(temp_user, request_content, user_id):
    """Sends message formatted."""

    snippet = request_content["snippet"]
    url = request_content["URL"]
    title = request_content["title"]
    parsed_url = urlparse(url=url)

    db_id = db_utils.save_snippet_to_db(url, snippet, user_id, title)

    embed = discord.Embed(
        url=url, colour=discord.Colour.random(), title=parsed_url.netloc
    )

    embed.add_field(name=f"# {db_id}", value=f"```{snippet}```")
    # embed.add_field(name=f"# {db_id}", value=f"\n**{snippet}**")
    # image_url = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"
    # print(f"{image_url=}")
    # embed.set_image(url=image_url)
    # embed.set_thumbnail(url=image_url)
    embed.set_footer(text=url)

    await temp_user.send(embed=embed)


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
