# pylint: disable=import-error, line-too-long
"""DB utils."""

import uuid

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

# create table if it does not exist.
cur.execute(
    """CREATE TABLE IF NOT EXISTS login_codes (
        code_id serial PRIMARY KEY,
        code varchar(255) UNIQUE,
        discord_user_id BIGINT NOT NULL,
        discord_user_name varchar(255)) NOT NULL"""
)


def create_code_key(discord_user_id, discord_user_name) -> str:
    """Creates codes for users to confirm discord for chrome extension"""

    # create new ey
    key = str(uuid.uuid4())

    cur.execute(
        "INSERT INTO login_codes (discord_user_id, code, discord_user_name) VALUES (%s, %s, %s)",
        (discord_user_id, key, discord_user_name),
    )
    return key


def query_db_by_code(code):
    """Queries the DB by code and returns discords user"""
    cur.execute(
        "SELECT discord_user_id FROM login_codes WHERE code = %(value)s",
        {"value": code},
    )
    return cur.fetchone()[0]


def invalidate_codes(discord_user_id) -> None:
    """Queries the DB by discord_user_id and deletes all codes"""
    cur.execute(
        "DELETE FROM login_codes WHERE discord_user_id = %(value)s",
        {"value": discord_user_id},
    )
