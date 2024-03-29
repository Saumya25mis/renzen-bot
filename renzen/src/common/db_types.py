"""DB dataclasses."""
import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class RenzenUserInfo:
    """Holds data from renzen_user_info table"""

    renzen_user_id: str  # PK
    renzen_user_name: str  # UNIQUE
    creation_timestamp: datetime.datetime
    renzen_email: str = ""
    password: str = ""  # unused for now


@dataclass(frozen=True)
class GithubUserInfo:
    """Holds data from github_user_info table"""

    github_username: str
    github_email: str
    renzen_user_id: str
    creation_timestamp: str


@dataclass(frozen=True)
class DiscordUserInfo:
    """Holds data from discord_user_info table"""

    discord_user_id: str  # PK
    renzen_user_id: str
    discord_user_name: str  # FK
    creation_timestamp: datetime.datetime


@dataclass(frozen=True)
class LoginCode:
    """Data from login_codes table."""

    code: str
    renzen_user_id: str
    creation_timestamp: datetime.datetime


@dataclass(frozen=True)
class Snippet:
    """Data from snippets table"""

    renzen_user_id: str  # FK
    snippet_id: str  # PK
    title: str
    url: str
    parsed_url: str
    snippet: str
    creation_timestamp: datetime.datetime


@dataclass(frozen=True)
class Page:
    """Data from pages table"""

    renzen_user_id: str  # FK

    page_id: str  # PK

    path: str
    fetch_url: str
    creation_timestamp: datetime.datetime


@dataclass(frozen=True)
class SnippetPageJunction:
    """Starred pages."""

    branch_name: str
    snippet_id: str  # FK
    renzen_user_id: str  # FK
    page_id: str  # FK
    creation_timestamp: datetime.datetime
