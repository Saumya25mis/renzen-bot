# pylint: disable=too-many-instance-attributes
"""DB return dataclasses."""
import datetime
from dataclasses import dataclass


# RESPONSE TYPES
@dataclass(frozen=True)
class VsExtSnippetProps:
    """VS Code Ext return data."""

    snippet_id: str
    renzen_user_id: str
    title: str
    snippet: str
    url: str
    parsed_url: str
    creation_timestamp: datetime.datetime
    path: str = ""  # only used for starred returns
    star_id: str = ""


# REQUEST TYPES
@dataclass(frozen=True)
class StarRequest:
    """Data received for star request."""

    renzen_user_id: str
    page_path: str
    snippet_id: str
    fetch_url: str
    req_type: bool  # true to star, false to not
    star_id: str = ""  # only for un-starring


@dataclass(frozen=True)
class ForwardRequest:
    """Data received for forward request."""

    login_code: str
    snippet: str
    url: str
    title: str


@dataclass(frozen=True)
class GetSnippetsRequest:
    """Data received for get snippets request"""

    login_code: str
    fetch_url: str
