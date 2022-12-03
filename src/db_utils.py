"""DB utils."""

import uuid
import datetime

import psycopg2
from src import secret_utils

conn = psycopg2.connect(
    database="postgres",
    user=secret_utils.DB_USERNAME,
    password=secret_utils.DB_PASSWORD,
    host=secret_utils.DB_ENDPOINT,
    port=secret_utils.DB_PORT,
    sslmode="require",
)

conn.autocommit = True

cur = conn.cursor()


# create user table if it does not exist.
cur.execute(
    """CREATE TABLE IF NOT EXISTS discord_user_info (
        discord_user_id BIGINT PRIMARY KEY,
        discord_user_name varchar(255),
        creation_timestamp timestamp NOT NULL DEFAULT NOW()
    )
    """
)

# create login_codes table if it does not exist.
# login codes have foreign keys to discord_user_info
cur.execute(
    """CREATE TABLE IF NOT EXISTS login_codes (
        code varchar(255) UNIQUE,
        discord_user_id BIGINT,
        creation_timestamp timestamp NOT NULL DEFAULT NOW(),
        CONSTRAINT fk_login_codes_discord_user_info
            FOREIGN KEY (discord_user_id)
                REFERENCES discord_user_info(discord_user_id)
                ON DELETE CASCADE
    )
    """
)

# (snippet_id, url, snippet, title, discord_user_id, creation_timestamp)

# create snippets table if it does not exist.
cur.execute(
    """CREATE TABLE IF NOT EXISTS snippets (
        snippet_id serial PRIMARY KEY,
        title TEXT,
        url TEXT,
        snippet TEXT,
        discord_user_id BIGINT,
        creation_timestamp timestamp NOT NULL DEFAULT NOW(),
        CONSTRAINT fk_snippets_discord_user_info
            FOREIGN KEY (discord_user_id)
                REFERENCES discord_user_info(discord_user_id)
                ON DELETE CASCADE
    )
    """
)


def create_code(discord_user_id, discord_user_name) -> str:
    """Creates codes for users to confirm discord for chrome extension"""

    # check if user has been add to discord_user_info table
    sql = """SELECT *
            FROM discord_user_info
            WHERE discord_user_id = (%s)
        """
    cur.execute(sql, (discord_user_id,))

    if not cur.fetchone():

        # user has not been added to discord_user_info table, so add them
        sql = """INSERT INTO discord_user_info
                (discord_user_id, discord_user_name) VALUES (%s, %s)
            """
        cur.execute(sql, (discord_user_id, discord_user_name))

    code = str(uuid.uuid4())  # create new code

    # add new code to login_codes table
    sql = """INSERT INTO login_codes (discord_user_id, code) VALUES (%s, %s)"""
    cur.execute(sql, (discord_user_id, code))

    return code  # return code to be sent to user


def query_db_by_date(date=None):
    """Query today."""

    if not date:
        date = str(datetime.datetime.now().date())

    print(f"Searching for {date}")

    sql = """select snippet_id, url, snippet, title, discord_user_id, creation_timestamp
        from   snippets
        where  creation_timestamp >= (%(value)s::timestamp)
        and    creation_timestamp < ((%(value)s::date)+1)::timestamp;
        """
    cur.execute(
        sql,
        {"value": date},
    )

    return cur.fetchall()


def query_db_by_code(code):
    """Queries the DB by code and returns discords user"""

    sql = """SELECT discord_user_id
            FROM login_codes WHERE code = %(value)s
        """
    cur.execute(
        sql,
        {"value": code},
    )

    fetched = cur.fetchone()
    if fetched:
        return fetched[0]
    return None


def invalidate_codes(discord_user_id) -> None:
    """Queries the DB by discord_user_id and deletes all codes"""

    sql = """DELETE FROM login_codes
            WHERE discord_user_id = %(value)s
        """
    cur.execute(
        sql,
        {"value": discord_user_id},
    )


def search_urls_by_str(search_string, discord_user_id):
    """Search urls and snippets by string."""

    sql = """SELECT snippet_id, url, snippet, title, discord_user_id, creation_timestamp
            FROM snippets
            WHERE url ILIKE %(search_string)s
            AND  discord_user_id =%(discord_user_id)s
        """

    cur.execute(
        sql, {"search_string": f"%{search_string}%", "discord_user_id": discord_user_id}
    )

    return cur.fetchall()


def search_snippets_by_str(search_string, discord_user_id):
    """Search urls and snippets by string."""

    sql = """SELECT snippet_id, url, snippet, title, discord_user_id, creation_timestamp
            FROM snippets
            WHERE snippet ILIKE %(search_string)s
            AND  discord_user_id =%(discord_user_id)s
        """

    cur.execute(
        sql, {"search_string": f"%{search_string}%", "discord_user_id": discord_user_id}
    )

    return cur.fetchall()


def save_snippet_to_db(url, snippet, discord_user_id, title):
    """Saves snippet to db."""

    sql = """INSERT INTO snippets
                (url, snippet, discord_user_id, title) VALUES (%s, %s, %s, %s)
                RETURNING snippet_id
            """
    cur.execute(sql, (url, snippet, discord_user_id, title))

    last_row_id = cur.fetchone()[0]

    return last_row_id
