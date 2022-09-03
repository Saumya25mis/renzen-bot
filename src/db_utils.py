# pylint: disable=import-error
"""DB utils."""

import logging
import psycopg2
import discord
from src import secret_utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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


def save_message_to_db(message: discord.Message):
    """Save message to db."""
    logger.info("Preparing to INSERT into DB")
    cur.execute(
        "INSERT INTO messages (author, content, channel) VALUES (%s, %s, %s)",
        (message.author, message.content, message.channel),
    )
    logger.info("Executed INSERT")
