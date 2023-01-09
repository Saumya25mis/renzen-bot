"""Bot utility functions."""
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import discord
from src.common import db_types

EMBED_MAX_SIZE = 6000
SNIPPET_FORWARD_MAX_SIZE = 1024
FIELD_VALUE_MAX_SIZE = 600
FIELD_NAME_MAX_SIZE = 256

MAX_SEARCH_SNIPPET_TEXT_LENGTH = 150


async def format_search_embed(
    snippet_matches: List[db_types.Snippet],
    search_for: Optional[str] = None,
    exclude_message_ids: Optional[List[str]] = None,
    title: str = "Formatted",
    description: str = "Search Results",
    author: str = "renzen",
) -> Tuple[List[str], List[discord.Embed]]:
    """Format search return results."""

    embeds: List[discord.Embed] = []  # all embeds to send
    embed: Optional[discord.Embed] = None

    found_message_ids: List[str] = []
    if not exclude_message_ids:
        exclude_message_ids = []

    for snippet in snippet_matches:

        # skip over messages already sent
        if snippet.snippet_id in exclude_message_ids:
            continue
        found_message_ids.append(snippet.snippet_id)

        # get sized correctly
        escaped_string = discord.utils.escape_markdown(snippet.snippet)
        bolded_string = ""
        if search_for:
            bolded_string = bold_substring(escaped_string, search_for)

        domain_link = f"**[{urlparse(url=snippet.url).netloc}]({snippet.url})** \n"
        value = (
            domain_link
            + (bolded_string or escaped_string)[0 : MAX_SEARCH_SNIPPET_TEXT_LENGTH - 5]
            + "...\n"
        )

        # check length of field value
        if len(value) > FIELD_VALUE_MAX_SIZE:
            value = value[0 : FIELD_VALUE_MAX_SIZE - 10] + "...\n"

        # check length of field name
        field_title = snippet.title
        if len(field_title) > FIELD_NAME_MAX_SIZE:
            field_title = field_title[0 : FIELD_NAME_MAX_SIZE - 3] + "..."

        # estimate size to determine whether to create an additional embed
        current_embed_length = len(embed) if embed else 0  # type: ignore
        est_new_size = current_embed_length + len(field_title) + len(value)

        if not embed or est_new_size >= EMBED_MAX_SIZE:
            # create new embed
            embed = discord.Embed(
                title=f"#{len(embeds)+1} {title}",
                description=description,
                colour=discord.Colour.random(),
            )
            embeds.append(embed)
            embed.set_author(name=author)

        # add field to current embed
        embed.add_field(name=field_title, value=value)

    return found_message_ids, embeds


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


async def send_formatted_discord_message(snippet: db_types.Snippet) -> discord.Embed:
    """Sends message formatted."""

    snippet_text = snippet.snippet

    # truncate snippet
    if len(snippet_text) >= SNIPPET_FORWARD_MAX_SIZE:
        snippet_text = snippet_text[0 : SNIPPET_FORWARD_MAX_SIZE - 3] + "..."

    parsed_url = urlparse(url=snippet.url)

    embed = discord.Embed(
        url=snippet.url, colour=discord.Colour.random(), title=parsed_url.netloc
    )

    embed.add_field(
        name=f"# {snippet.snippet_id}: {snippet.title}", value=f"```{snippet_text}```"
    )
    embed.set_footer(text=snippet.url)

    return embed
