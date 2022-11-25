# pylint: disable=import-error, line-too-long
"""DB utils."""

# import logging
import uuid
import psycopg2

# import discord
from src import secret_utils

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

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

# check if table exists
# try:
#     cur.execute(
#         "select exists(select * from information_schema.tables where table_name=%s)",
#         ("codes",),
#     )
#     exists = cur.fetchone()[0]
#     print(f"table exists: {exists}")
# except psycopg2.Error as e:  # pylint:disable=invalid-name
#     # create table
#     cur.execute("CREATE TABLE codes (discord_user_id: int, code: varchar(255))")
#     print("Create table")
cur.execute(
    "CREATE TABLE IF NOT EXISTS codes (code_id serial PRIMARY KEY, discord_user_id BIGINT NOT NULL, code varchar(255) UNIQUE)"
)


def create_code_key(user_id):
    """Creates codes for users to confirm discord for chrome extension"""
    key = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO codes (discord_user_id, code) VALUES (%s, %s)",
        (user_id, key),
    )
    return key


# def save_message_to_db(message: discord.Message):
#     """Save message to db."""
#     logger.info("Preparing to INSERT into DB")
#     cur.execute(
#         "INSERT INTO messages (author, content, channel) VALUES (%s, %s, %s)",
#         (message.author.name, message.content, message.channel.name),
#     )
#     logger.info("Executed INSERT")
