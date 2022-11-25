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

cur.execute(
    "CREATE TABLE IF NOT EXISTS login_codes (code_id serial PRIMARY KEY, discord_user_id BIGINT NOT NULL, code varchar(255) UNIQUE)"
)


def create_code_key(user_id):
    """Creates codes for users to confirm discord for chrome extension"""
    key = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO login_codes (discord_user_id, code) VALUES (%s, %s)",
        (user_id, key),
    )
    return key


def query_db_by_code(code):
    """Queries the DB by code and returns discords user"""
    cur.execute(
        "SELECT discord_user_id FROM login_codes WHERE code = %(value)s",
        {"value": code},
    )
    return cur.fetchone()[0]
