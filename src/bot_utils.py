# pylint: disable=import-error, no-member, unused-argument, unused-variable, too-many-locals, too-many-arguments
"""Bot utility functions."""
from urllib.parse import urlparse
import discord
from src import db_utils

EMBED_MAX_SIZE = 6000
FIELD_VALUE_MAX_SIZE = 1024
FIELD_NAME_MAX_SIZE = 256


async def format_search_embed(
    interaction,
    snippet_matches,
    search_for=None,
    exclude_message_ids=None,
    title="Formatted",
    description="Search Results",
    author="renzen",
):
    """Format search return results."""
    print(f"{snippet_matches=}")

    embeds = []  # all embeds to send
    embed = None

    found_message_ids = []
    if not exclude_message_ids:
        exclude_message_ids = []

    for snippet in snippet_matches:

        message_id = snippet[0]
        url = snippet[1]
        original_value = snippet[2]
        url_title = f"**{snippet[3]}** \n\n"
        escaped_string = ""
        bolded_string = ""

        # skip over messages already sent
        if message_id in exclude_message_ids:
            continue
        found_message_ids.append(message_id)

        # get sized correctly
        escaped_string = discord.utils.escape_markdown(original_value)
        if search_for:
            bolded_string = bold_substring(escaped_string, search_for)

        value = url_title + (bolded_string or escaped_string)

        if len(value) > FIELD_VALUE_MAX_SIZE:
            value = value[0 : FIELD_VALUE_MAX_SIZE - 3] + "..."

        est_new_size = (len(embed) if embed else 0) + len(url) + len(value)

        if not embed or est_new_size >= EMBED_MAX_SIZE:
            # create new embed
            print("Creating new embed.")
            embed = discord.Embed(
                title=f"#{len(embeds)+1} {title}",
                description=description,
                colour=discord.Colour.random(),
            )
            embeds.append(embed)
            embed.set_author(name=author)

        embed.add_field(name=url, value=value)

    for embed in embeds:
        await interaction.followup.send(embed=embed)

    return found_message_ids


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

    return bolded_string


async def send_formatted_discord_message(temp_user, request_content, user_id):
    """Sends message formatted."""

    snippet = request_content["snippet"]

    # truncate snippet
    if len(snippet) >= FIELD_VALUE_MAX_SIZE:
        snippet = snippet[0 : FIELD_VALUE_MAX_SIZE - 3] + "..."

    url = request_content["URL"]
    title = request_content["title"]
    parsed_url = urlparse(url=url)

    db_id = db_utils.save_snippet_to_db(url, snippet, user_id, title)

    embed = discord.Embed(
        url=url, colour=discord.Colour.random(), title=parsed_url.netloc
    )

    embed.add_field(name=f"# {db_id}: {title}", value=f"```{snippet}```")
    embed.set_footer(text=url)

    await temp_user.send(embed=embed)
