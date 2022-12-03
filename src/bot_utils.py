"""Bot utility functions."""
from typing import List, Optional, Union
from urllib.parse import urlparse
import discord
from src import db_utils

EMBED_MAX_SIZE = 6000
FIELD_VALUE_MAX_SIZE = 1024
FIELD_NAME_MAX_SIZE = 256


async def format_search_embed(
    interaction: discord.Interaction,
    snippet_matches: List[db_utils.Snippets],
    search_for: Optional[str] = None,
    exclude_message_ids: Optional[List[str]] = None,
    title: str = "Formatted",
    description: str = "Search Results",
    author: str = "renzen",
) -> List[str]:
    """Format search return results."""
    print(f"{snippet_matches=}")

    embeds: List[discord.Embed] = []  # all embeds to send
    embed: Optional[discord.Embed] = None

    found_message_ids: List[str] = []
    if not exclude_message_ids:
        exclude_message_ids = []

    for snippet in snippet_matches:

        url_title = f"**{snippet.title}** \n\n"
        escaped_string = ""
        bolded_string = ""

        # skip over messages already sent
        if snippet.snippet_id in exclude_message_ids:
            continue
        found_message_ids.append(snippet.snippet_id)

        # get sized correctly
        escaped_string = discord.utils.escape_markdown(snippet.snippet)
        if search_for:
            bolded_string = bold_substring(escaped_string, search_for)

        value = url_title + (bolded_string or escaped_string)

        if len(value) > FIELD_VALUE_MAX_SIZE:
            value = value[0 : FIELD_VALUE_MAX_SIZE - 3] + "..."

        est_new_size = (len(embed) if embed else 0) + len(snippet.url) + len(value)  # type: ignore

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

        embed.add_field(name=snippet.url, value=value)

    for embed in embeds:
        await interaction.followup.send(embed=embed)

    return found_message_ids


def bold_substring(value: str, substring: str) -> str:
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


async def send_formatted_discord_message(
    temp_user: discord.User, request_content: dict[str, str], user_id: Union[str, int]
) -> None:
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
