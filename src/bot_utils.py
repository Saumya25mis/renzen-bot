# pylint: disable=import-error, no-member, unused-argument, unused-variable, too-many-locals
"""Bot utility functions."""
from urllib.parse import urlparse
import discord
from src import db_utils

FULL_MAX_SIZE = 5000


async def format_search_embed(
    interaction,
    snippet_matches,
    search_for=None,
    exclude_message_ids=None,
    title="Formatted",
):
    """Format search return results."""
    print(f"{snippet_matches=}")

    size = 6  # length of bot name
    embeds = []  # all embeds to send
    embed = None

    found_message_ids = []
    if not exclude_message_ids:
        exclude_message_ids = []

    for snippet in snippet_matches:
        message_id = snippet[0]

        # skip over messages already sent
        if message_id in exclude_message_ids:
            continue
        found_message_ids.append(message_id)

        url = snippet[1]
        original_value = snippet[2]
        url_title = f"**{snippet[3]}** \n\n"

        # get sized correctly

        # do initail trim
        trimmed_string = trim_string(original_value)
        escaped_string = discord.utils.escape_markdown(trimmed_string)

        if len(escaped_string) > 1000:
            # re-trim string
            value = discord.utils.escape_markdown(
                trim_string(trimmed_string, 1000 - (len(escaped_string) - 1000))
            )
        else:
            value = escaped_string

        if not value:
            continue

        est_new_size = size + len(url) + len(value) + len(url_title)

        if not embed or est_new_size >= FULL_MAX_SIZE:
            # create new embed
            print("Creating new embed.")
            embed = discord.Embed(
                title=title,
                description="Search Results",
                colour=discord.Colour.random(),
            )
            embeds.append(embed)
            embed.set_author(name="renzen")
            size = 6

        # adds more characters, but for now should be neglible
        if search_for:
            value = bold_substring(trim_string(value), search_for)

        size += len(url) + len(value)
        embed.add_field(name=url, value=url_title + value)

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

    # debug
    print(locals())

    return bolded_string


def trim_string(string, max_chars=1000):
    """Trims string."""
    return string[0 : min(len(string), max_chars)]


async def send_formatted_discord_message(temp_user, request_content, user_id):
    """Sends message formatted."""

    truncate = 1000

    snippet = request_content["snippet"]

    # truncate snippet
    if len(snippet) >= truncate:
        snippet = snippet[0 : truncate - 3] + "..."

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
