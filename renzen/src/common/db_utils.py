# pylint: disable=invalid-name
"""DB utils."""
# import itertools
import datetime
import logging
import os
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from src.common.api_types import VsExtSnippetProps
from src.common.db_tables import cur
from src.common.db_types import (
    DiscordUserInfo,
    GithubUserInfo,
    LoginCode,
    RenzenUserInfo,
    Snippet,
)

logger = logging.getLogger(__name__)
CURRENT_ENVIRONMENT = os.getenv("CURRENT_ENVIRONMENT")


class DBUtilsException(Exception):
    """DB Utils Except -> None:"""

    def __init__(self) -> None:
        super()


# CHROME EXTENSION ACTIONS


def save_snippet_to_db(
    url: str, snippet: str, renzen_user_id: Union[str, int], title: str
) -> Optional[str]:
    """Saves snippet to db."""

    logger.info("Saving snippet in db for %s", (url))

    # generate parsed urls
    parsed_url = urlparse(url=url).netloc

    sql = """
    INSERT INTO snippets
    (url, snippet, renzen_user_id, title, parsed_url)
    VALUES (%(url)s, %(snippet)s, %(renzen_user_id)s, %(title)s, %(parsed_url)s)
    RETURNING snippet_id
    """

    cur.execute(
        sql,
        {
            "url": url,
            "snippet": snippet,
            "renzen_user_id": renzen_user_id,
            "title": title,
            "parsed_url": parsed_url,
        },
    )

    fetched = cur.fetchone()

    return str(fetched["snippet_id"]) if fetched else None


# VS EXTENSION ACTIONS


def star(
    renzen_user_id: str,
    path: str,
    snippet_id: str,
    fetch_url: str,
    req_type: bool,
    star_id: Optional[str] = None,
) -> Optional[str]:
    """Associates snippet with page"""

    logger.warning(f"{path=}")
    logger.warning(f"{req_type=}")

    if req_type is False:
        if not star_id:
            raise DBUtilsException
        # attempt to delete star instead of add
        logger.warning("Deleting star")
        sql = """
        DELETE FROM snippet_page_junction
        WHERE star_id = %(star_id)s
        """

        values: Dict[Any, Any] = {"star_id": int(star_id)}

        cur.execute(sql, values)

        return ""

    # search for page by path
    sql = """
    SELECT page_id FROM pages
    WHERE renzen_user_id=%(renzen_user_id)s
    AND path=%(path)s
    AND fetch_url=%(fetch_url)s
    """

    values = {
        "renzen_user_id": renzen_user_id,
        "path": path,
        "fetch_url": fetch_url,
    }

    logger.warning(f"{values=}")

    cur.execute(sql, values)
    fetched = cur.fetchone()

    if not fetched:
        # create page in table since it doesn't exist
        sql = """
        INSERT INTO pages
        (renzen_user_id, path, fetch_url)
        VALUES (%(renzen_user_id)s, %(path)s, %(fetch_url)s)
        RETURNING page_id
        """

        values = {
            "renzen_user_id": renzen_user_id,
            "path": path,
            "fetch_url": fetch_url,
        }

        cur.execute(sql, values)
        fetched = cur.fetchone()

    if not fetched:
        raise DBUtilsException

    # create star/asscociation
    sql = """
    INSERT INTO snippet_page_junction (renzen_user_id, page_id, snippet_id, branch_name)
    VALUES (%(renzen_user_id)s, %(page_id)s, %(snippet_id)s, %(branch_name)s)
    RETURNING star_id
    """

    snippet = load_snippet_from_db(snippet_id)

    if snippet:

        cur.execute(
            sql,
            {
                "renzen_user_id": renzen_user_id,
                "page_id": fetched["page_id"],
                "snippet_id": snippet_id,
                "branch_name": "None",
            },
        )

        fetched = cur.fetchone()

        return_value = str(fetched["star_id"]) if fetched else None
        logger.info(f"{return_value=}")
        return return_value

    logger.info(None)
    return None


# SEARCHES


def vs_ext_get_mapped_paths_to_snippets(
    renzen_user_id: str, fetch_url: str
) -> List[VsExtSnippetProps]:
    """Get data by user and repo, and stars so VS CODE ext can correctly sort snippets."""

    # return which current users snippets are starred to which pages in repository
    sql = """
    SELECT s.snippet_id, s.title, s.snippet, s.url, s.parsed_url, p.path, s.creation_timestamp, s.renzen_user_id, spj.star_id
    FROM snippet_page_junction spj
    JOIN snippets s ON s.snippet_id = spj.snippet_id
    JOIN pages p ON p.page_id = spj.page_id
    WHERE p.fetch_url=%(fetch_url)s
    AND spj.renzen_user_id = %(renzen_user_id)s
    """

    values = {"renzen_user_id": renzen_user_id, "fetch_url": fetch_url}

    cur.execute(sql, values)
    fetched = cur.fetchall()

    # logger.warning(f'vs_ext_get_mapped_paths_to_snippets {fetched=}')
    # logger.warning(locals())
    return [VsExtSnippetProps(**fetch) for fetch in fetched]


def vs_ext_get_all_user_snippets(renzen_user_id: str) -> List[Snippet]:
    """Gets all the users snippets they have saved"""

    sql = """
    SELECT renzen_user_id, snippet_id, title, url, parsed_url, snippet, creation_timestamp, renzen_user_id
    FROM snippets
    WHERE renzen_user_id = %(renzen_user_id)s
    """

    values = {"renzen_user_id": renzen_user_id}

    cur.execute(sql, values)
    fetched = cur.fetchall()

    # logger.warning(f"vs_ext_get_all_user_snippets {fetched=}")
    # logger.warning(locals())
    return [Snippet(**fetch) for fetch in fetched]


def get_github_user_by_username(github_username: str) -> Optional[GithubUserInfo]:
    """Get github user by email"""

    sql = """
    SELECT github_username, github_email, renzen_user_id, creation_timestamp
    FROM github_user_info
    WHERE github_username=%(github_username)s
    """
    values = {"github_username": github_username}
    cur.execute(sql, values)
    fetched = cur.fetchone()

    return GithubUserInfo(**fetched) if fetched else None


# ID CONVERSIONS


def get_renzen_user_by_discord_id(
    discord_user_id: Union[str, int]
) -> Optional[RenzenUserInfo]:
    """Gets renzen id from discord id."""

    sql = """
    Select ri.renzen_user_id, ri.renzen_user_name, ri.creation_timestamp, ri.renzen_email
    FROM discord_user_info di
    JOIN renzen_user_info ri
    ON ri.renzen_user_id = di.renzen_user_id
    WHERE discord_user_id = %(discord_user_id)s
    """

    values = {"discord_user_id": discord_user_id}

    cur.execute(sql, values)
    fetched = cur.fetchone()

    return RenzenUserInfo(**fetched) if fetched else None


def get_discord_user_by_renzen_user_id(
    renzen_user_id: Union[str, int]
) -> Optional[DiscordUserInfo]:
    """Queries the DB by code and returns discords user"""

    logger.info("Querying by renzen_user_id")

    sql = """
    SELECT discord_user_id, renzen_user_id, discord_user_name, creation_timestamp
    FROM discord_user_info WHERE renzen_user_id = %(renzen_user_id)s
    """

    values = {"renzen_user_id": renzen_user_id}

    cur.execute(sql, values)
    fetched = cur.fetchone()

    return DiscordUserInfo(**fetched) if fetched else None


def get_renzen_user_by_code(code: Union[str, int]) -> Optional[RenzenUserInfo]:
    """Queries the DB by code and returns renzen user"""

    logger.info(f"Querying by code {code=}")

    sql = """
    SELECT ri.renzen_user_id, ri.creation_timestamp, ri.renzen_user_name, ri.renzen_email
    FROM login_codes lc
    JOIN renzen_user_info ri
    ON lc.renzen_user_id = ri.renzen_user_id
    WHERE lc.code = %(code)s
    """

    values = {"code": code}

    cur.execute(sql, values)
    fetched = cur.fetchone()

    return RenzenUserInfo(**fetched) if fetched else None


def get_renzen_user_by_username(username: Union[str, int]) -> Optional[RenzenUserInfo]:
    """Queries the DB by username and returns renzen user"""

    logger.info("Querying by username")

    sql = """
    SELECT renzen_user_id, creation_timestamp, renzen_user_name, renzen_email
    FROM renzen_user_info
    WHERE renzen_user_name = %(username)s
    """

    values = {"username": username}

    cur.execute(sql, values)
    fetched = cur.fetchone()

    return RenzenUserInfo(**fetched) if fetched else None


# DISCORD BOT ACTIONS


class LoginSource(Enum):
    """Login Sources."""

    VS_CODE = "vs_code"
    DISCORD = "discord"
    CHROME = "chrome"


def login_or_create_renzen_user_with_github_oauth(
    github_username: str,
    github_email: str,
    login_source: LoginSource,
    source_id: Optional[str] = None,
    source_name: Optional[str] = None,
) -> LoginCode:
    """Creates a renzen user with github credentials.
    Source id is to associate with discord user for now.
    """

    github_user_info = get_github_user_by_username(github_username=github_username)

    if not github_user_info:
        renzen_user_info = create_renzen_user_info(
            github_username=github_username, github_email=github_email
        )
        github_user_info = create_github_user_info(
            github_username=github_username,
            github_email=github_email,
            renzen_user_id=renzen_user_info.renzen_user_id,
        )

    renzen_user_id = github_user_info.renzen_user_id

    if login_source == LoginSource.DISCORD:
        if source_id and source_name:
            discord_user_info = get_discord_user_by_renzen_user_id(
                renzen_user_id=renzen_user_id
            )
            if not discord_user_info:
                create_discord_user_info(
                    renzen_user_id=renzen_user_id,
                    discord_user_id=source_id,
                    discord_user_name=source_name,
                )
        else:
            raise DBUtilsException
    elif login_source == LoginSource.VS_CODE:
        pass

    return create_one_time_code(renzen_user_id=renzen_user_id)


def create_renzen_user_info(github_username: str, github_email: str) -> RenzenUserInfo:
    """Creates code for vs code user"""

    # create renzen user
    # this is currently the only way to create a renzen user
    sql = """
    INSERT INTO renzen_user_info (renzen_user_name, renzen_email)
    VALUES (%(renzen_user_name)s, %(renzen_email)s)
    RETURNING renzen_user_id, renzen_user_name, renzen_email, creation_timestamp
    """
    values = {"renzen_user_name": github_username, "renzen_email": github_email}
    cur.execute(sql, values)
    fetched = cur.fetchone()
    renzen_user_info = RenzenUserInfo(**fetched) if fetched else None

    if not renzen_user_info:
        raise DBUtilsException
    return renzen_user_info


def create_github_user_info(
    github_username: str, github_email: str, renzen_user_id: str
) -> GithubUserInfo:
    """Creates code for vs code user"""

    # create github user
    sql = """
    INSERT INTO github_user_info (github_username, github_email, renzen_user_id)
    VALUES (%(github_username)s, %(github_email)s, %(renzen_user_id)s)
    RETURNING github_username, github_email, renzen_user_id, creation_timestamp
    """
    values = {
        "github_username": github_username,
        "github_email": github_email,
        "renzen_user_id": renzen_user_id,
    }
    cur.execute(sql, values)
    fetched = cur.fetchone()

    github_user_info = GithubUserInfo(**fetched) if fetched else None

    if not github_user_info:
        raise DBUtilsException
    return github_user_info


def create_one_time_code(renzen_user_id: Union[str, int]) -> LoginCode:
    """Creates codes for users to confirm discord for chrome extension"""

    logger.info("Generating code for %s", (renzen_user_id))

    code = str(uuid.uuid4())  # create new code

    # add new code to login_codes table
    sql = """
    INSERT INTO login_codes (renzen_user_id, code)
    VALUES (%(renzen_user_id)s, %(code)s)
    RETURNING code, renzen_user_id, creation_timestamp
    """

    values = {"renzen_user_id": renzen_user_id, "code": code}

    cur.execute(sql, values)
    fetched = cur.fetchone()
    if not fetched:
        raise DBUtilsException
    login_code = LoginCode(**fetched)

    return login_code


def get_discord_user_info_by_discord_id(
    discord_user_id: Union[str, int]
) -> Optional[DiscordUserInfo]:
    """Get discord user info by discord id"""
    sql = """
    SELECT *
    FROM discord_user_info
    WHERE discord_user_id = (%(discord_user_id)s)
    """

    values: Dict[str, Union[str, int]] = {"discord_user_id": discord_user_id}

    cur.execute(sql, values)
    fetched = cur.fetchone()
    return DiscordUserInfo(**fetched) if fetched else None


def create_discord_user_info(
    discord_user_id: Union[str, int],
    discord_user_name: str,
    renzen_user_id: str,
) -> DiscordUserInfo:
    """Create discord user info."""
    sql = """
        INSERT INTO discord_user_info
        (discord_user_id, discord_user_name, renzen_user_id)
        VALUES (%(discord_user_id)s, %(discord_user_name)s, %(renzen_user_id)s)
        RETURNING discord_user_name, discord_user_id, renzen_user_id, creation_timestamp
        """

    values = {
        "discord_user_id": discord_user_id,
        "discord_user_name": discord_user_name,
        "renzen_user_id": renzen_user_id,
    }

    cur.execute(sql, values)
    fetched = cur.fetchone()
    if not fetched:
        raise DBUtilsException

    return DiscordUserInfo(**fetched)


def create_renzen_user_from_discord_user_name(discord_user_name: str) -> RenzenUserInfo:
    """Creeat renzen user from discord user name"""
    sql = """
            INSERT INTO renzen_user_info
            (renzen_user_name) VALUES (%(renzen_user_name)s)
            RETURNING renzen_user_id, renzen_user_name, creation_timestamp
            """

    values = {"renzen_user_name": discord_user_name}

    cur.execute(sql, values)

    fetched = cur.fetchone()
    if not fetched:
        raise DBUtilsException
    renzen_user_info = RenzenUserInfo(**fetched)

    return renzen_user_info


def load_snippet_from_db(db_id: str) -> Optional[Snippet]:
    """Loads snippet using ID (current used by bot to load from queue)"""

    logger.info("Loading snippet from db for id %s", (db_id))

    sql = """
    SELECT snippet_id, url, snippet, title, renzen_user_id, creation_timestamp, parsed_url
    FROM snippets
    WHERE snippet_id=%(snippet_id)s"""

    values = {"snippet_id": db_id}

    cur.execute(sql, values)

    fetched = cur.fetchone()

    return Snippet(**fetched) if fetched else None


def query_db_by_date(
    renzen_user_id: Union[str, int], date: Optional[str] = None
) -> List[Snippet]:
    """Query today.
    need to do by user also
    """

    logger.info("Querying by date")

    if not date:
        date = str(datetime.datetime.now().date())

    sql = """
    SELECT snippet_id, url, snippet, title, renzen_user_id, creation_timestamp, parsed_url
    FROM snippets
    WHERE creation_timestamp >= (%(value)s::timestamp)
    AND creation_timestamp < (((%(value)s::date)+1)::timestamp)
    AND renzen_user_id =%(renzen_user_id)s
    """

    values = {"value": date, "renzen_user_id": renzen_user_id}

    cur.execute(
        sql,
        values,
    )

    return [Snippet(**fetch) for fetch in cur.fetchall()]


def search_urls_by_str(
    search_string: str, renzen_user_id: Union[str, int]
) -> List[Snippet]:
    """Search urls and snippets by string."""

    logger.info("Searching in urls for %s", (search_string))

    sql = """
    SELECT snippet_id, url, snippet, title, renzen_user_id, creation_timestamp, parsed_url
    FROM snippets
    WHERE url ILIKE %(search_string)s
    AND  renzen_user_id =%(renzen_user_id)s
    """

    values = {"search_string": f"%{search_string}%", "renzen_user_id": renzen_user_id}

    cur.execute(sql, values)

    return [Snippet(**fetch) for fetch in cur.fetchall()]


def search_snippets_by_str(
    search_string: str, renzen_user_id: Union[str, int]
) -> List[Snippet]:
    """Search urls and snippets by string."""

    logger.info("Searching in snippets for %s", (search_string))

    sql = """
    SELECT snippet_id, url, snippet, title, renzen_user_id, creation_timestamp, parsed_url
    FROM snippets
    WHERE snippet ILIKE %(search_string)s
    AND  renzen_user_id =%(renzen_user_id)s
    """

    cur.execute(
        sql, {"search_string": f"%{search_string}%", "renzen_user_id": renzen_user_id}
    )

    return [Snippet(**fetch) for fetch in cur.fetchall()]


def invalidate_codes(renzen_user_id: Union[str, int]) -> None:
    """Queries the DB by discord_user_id and deletes all codes"""

    logger.info("Invalidating codes for %s", renzen_user_id)

    sql = """DELETE FROM login_codes
            WHERE renzen_user_id = %(value)s
        """
    cur.execute(
        sql,
        {"value": renzen_user_id},
    )


def invalidate_code(code: Union[str, int]) -> None:
    """Queries the DB by discord_user_id and deletes all codes"""

    logger.info("Invalidating code %s", code)

    sql = """DELETE FROM login_codes
            WHERE code = %(code)s
        """
    cur.execute(
        sql,
        {"code": code},
    )
