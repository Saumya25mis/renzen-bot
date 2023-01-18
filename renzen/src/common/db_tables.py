"""DB tables."""
import logging
import os

import psycopg2
import psycopg2.extras
from src.common import secret_utils

logger = logging.getLogger(__name__)
CURRENT_ENVIRONMENT = os.getenv("CURRENT_ENVIRONMENT")


# get access to aws postgres
conn = psycopg2.connect(
    database=secret_utils.DB_DB,
    user=secret_utils.DB_USERNAME,
    password=secret_utils.DB_PASSWORD,
    host=secret_utils.DB_ENDPOINT,
    port=secret_utils.DB_PORT,
    # sslmode="require",
)

conn.autocommit = True

cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# RENZEN_USER_INFO
cur.execute(
    """CREATE TABLE IF NOT EXISTS renzen_user_info (

        renzen_user_id uuid DEFAULT gen_random_uuid() PRIMARY KEY,

        renzen_user_name varchar(255) UNIQUE,
        renzen_email varchar(255) UNIQUE,
        password varchar(255),

        creation_timestamp timestamp NOT NULL DEFAULT NOW()
    )
    """
)

# GITHUB_USER_INFO
cur.execute(
    """CREATE TABLE IF NOT EXISTS github_user_info (
        github_username varchar(255) UNIQUE PRIMARY KEY,
        github_email varchar(255),
        renzen_user_id uuid REFERENCES renzen_user_info NOT NULL,
        creation_timestamp timestamp NOT NULL DEFAULT NOW()
    )
    """
)


# DISCORD_USER_INFO
cur.execute(
    """CREATE TABLE IF NOT EXISTS discord_user_info (

        discord_user_id BIGINT PRIMARY KEY,
        renzen_user_id uuid REFERENCES renzen_user_info NOT NULL,
        discord_user_name varchar(255),
        creation_timestamp timestamp NOT NULL DEFAULT NOW()
    )
    """
)

# LOGIN_CODES
cur.execute(
    """CREATE TABLE IF NOT EXISTS login_codes (

        code varchar(255) PRIMARY KEY,
        creation_timestamp timestamp NOT NULL DEFAULT NOW(),
        renzen_user_id uuid REFERENCES renzen_user_info ON DELETE CASCADE
    )
    """
)

# SNIPPETS -- snippets saved from internet
cur.execute(
    """CREATE TABLE IF NOT EXISTS snippets (

        renzen_user_id uuid REFERENCES renzen_user_info ON DELETE CASCADE,
        snippet_id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
        title TEXT,
        url TEXT,
        parsed_url TEXT,
        snippet TEXT,
        creation_timestamp timestamp NOT NULL DEFAULT NOW()
    )
    """
)

# PAGES -- files in a repository
cur.execute(
    """CREATE TABLE IF NOT EXISTS pages (

        page_id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
        renzen_user_id uuid REFERENCES renzen_user_info ON DELETE CASCADE,
        path TEXT,
        fetch_url TEXT,
        creation_timestamp timestamp NOT NULL DEFAULT NOW(),

        -- index to make sure duplicate pages in the same repository can't exist for the same user
        UNIQUE (path, fetch_url, renzen_user_id)
    )
    """
)

# SNIPPET_PAGE_JUNCTION -- many to many snippets to pages
cur.execute(
    """CREATE TABLE IF NOT EXISTS snippet_page_junction (

        star_id serial PRIMARY KEY,
        renzen_user_id uuid REFERENCES renzen_user_info ON DELETE CASCADE,
        page_id uuid REFERENCES pages(page_id) ON DELETE CASCADE,
        snippet_id uuid REFERENCES snippets(snippet_id) ON DELETE CASCADE,
        creation_timestamp timestamp NOT NULL DEFAULT NOW(),
        branch_name TEXT,

        -- index to make sure duplicate stars can't exist for the same page and snippet for user
        UNIQUE (page_id, snippet_id, renzen_user_id)
    )
    """
)
