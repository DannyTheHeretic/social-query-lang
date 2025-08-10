# Imports
import json

from pyodide.http import FetchResponse, pyfetch  # The system we will actually use


class PyfetchSession:
    """Pyfetch Session, emulating the request Session."""

    def __init__(self, headers: dict | None = None) -> None:
        """Pyfetch Session, emulating the request Session."""
        self.default_headers = headers or {}

    async def get(self, url: str, headers: dict | None = None) -> FetchResponse:
        """Get request for the pyfetch."""
        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)
        return await pyfetch(
            url,
            method="GET",
            headers=merged_headers,
        )

    async def post(
        self,
        url: str,
        obj: dict | None = "",
        data: dict | None = None,
        headers: dict | None = None,
    ) -> FetchResponse:
        """Post request."""
        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)
        return await pyfetch(
            url,
            method="POST",
            headers=merged_headers,
            body=json.dumps(obj) if isinstance(obj, dict) else data,
        )


class BskySession:
    """Class to etablish an auth session."""

    def __init__(self, username: str, password: str) -> None:
        # Bluesky credentials
        self.username = username
        self.password = password
        self.pds_host = "https://bsky.social"
        # Instance client
        self.client = PyfetchSession()
        # Access token
        self.access_jwt = None
        # Refresh token
        self.refresh_jwt = None

    async def login(self) -> None:
        """Create an authenticated session and save tokens."""
        endpoint = f"{self.pds_host}/xrpc/com.atproto.server.createSession"
        session_info = await self.client.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            obj={
                "identifier": self.username,
                "password": self.password,
            },
        )
        session_info = await session_info.json()
        self.access_jwt = session_info["accessJwt"]
        self.refresh_jwt = session_info["refreshJwt"]
        self.client.default_headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_jwt}",
            },
        )

    async def get_profile(self) -> dict:
        """Get a user profile."""
        endpoint = f"{self.pds_host}/xrpc/app.bsky.actor.getProfile?actor={self.username}"
        response = await self.client.get(
            endpoint,
        )
        val = await response.json()
        print(val)
        return val

    def search(self, query: str) -> dict:
        """Search Bluesky."""
        endpoint = f"{self.pds_host}/xrpc/app.bsky.actor.searchActors?q={query}"
        return self.client.get(
            endpoint,
        ).json()

    def get_author_feed(self, actor: str) -> dict:
        """Get a specific user feed."""
        endpoint = f"{self.pds_host}/xrpc/app.bsky.feed.getAuthorFeed?actor={actor}"
        print(endpoint)
        return self.client.get(
            endpoint,
        ).json()
