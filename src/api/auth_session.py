# Imports
import json
from typing import Literal

from pyodide.http import FetchResponse, pyfetch  # The system we will actually use

LIMIT = 50


class PyfetchSession:
    """Pyfetch Session, emulating the request Session."""

    def __init__(self, headers: dict | None = None) -> None:
        """Pyfetch Session, emulating the request Session."""
        self.default_headers = headers or {}

    async def get(self, url: str, headers: dict | None = None) -> FetchResponse:
        """Get request for the pyfetch.

        Args:
            url (str): The Endpoint to hit
            headers (dict | None, optional): Any headers that will get added to the request. Defaults to "".

        Returns:
            FetchResponse: The return data from the request

        """
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
        data: str | dict | None = "",
        headers: dict | None = None,
    ) -> FetchResponse:
        """Post request.

        Args:
            url (str): The Endpoint to hit
            data (str | dict | None, optional): A dictionary or string to use for the body. Defaults to "".
            headers (dict | None, optional): Any headers that will get added to the request. Defaults to "".

        Returns:
            FetchResponse: The return data from the request

        """
        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)
        return await pyfetch(
            url,
            method="POST",
            headers=merged_headers,
            body=json.dumps(data) if isinstance(data, dict) else data,
        )


class BskySession:
    """Class to establish an auth session."""

    def __init__(self, username: str, password: str) -> None:
        # Bluesky credentials
        self.username = username
        self.password = password
        self.pds_host = "https://public.api.bsky.app"
        # Instance client
        self.client = PyfetchSession()
        # Access token
        self.access_jwt = None
        # Refresh token
        self.refresh_jwt = None

    async def login(self) -> None:
        """Create an authenticated session and save tokens."""
        endpoint: str = "https://bsky.social/xrpc/com.atproto.server.createSession"
        session_info: FetchResponse = await self.client.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            data={
                "identifier": self.username,
                "password": self.password,
            },
        )
        session_info: dict = await session_info.json()
        try:
            self.access_jwt: str = session_info["accessJwt"]
            self.refresh_jwt: str = session_info["refreshJwt"]
            self.did: str = session_info["did"]
            self.handle: str = session_info["handle"]
            self.pds_host = "https://bsky.social"
            self.client.default_headers.update(
                {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.access_jwt}",
                },
            )
        except KeyError:
            # TODO: Handle the error on the front end
            return False
        else:
            return True

    async def refresh_token(self) -> None:
        """Refresh the token."""
        endpoint = f"{self.pds_host}/xrpc/com.atproto.server.refreshSession"

        session_info = await self.client.post(
            endpoint, data="", headers={"Authorization": f"Bearer {self.refresh_jwt}"}
        )
        session_info = await session_info.json()
        self.access_jwt = session_info["accessJwt"]
        self.refresh_jwt = session_info["refreshJwt"]
        self.did = session_info["did"]

        self.client.default_headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_jwt}",
            },
        )

    ### Start of the actual endpoints -> https://docs.bsky.app/docs/api/at-protocol-xrpc-api
    async def get_preferences(self) -> dict:
        """Get the logged in users preferences."""
        endpoint = f"{self.pds_host}/xrpc/app.bsky.actor.getPreferences"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def get_profile(self, actor: str) -> dict:
        """Get a user profile."""
        # If no actor specified and we're authenticated, use our handle
        if actor is None:
            if hasattr(self, "handle") and self.handle:
                actor = self.handle
            else:
                # Return special error object for stealth mode
                return {"stealth_error": True}

        endpoint = f"{self.pds_host}/xrpc/app.bsky.actor.getProfile?actor={actor}"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def get_suggestions(self, limit: int | None = None, cursor: str = "") -> dict:
        """Get the logged in users suggestion."""
        if limit is None:
            limit = LIMIT

        endpoint = f"{self.pds_host}/xrpc/app.bsky.actor.getSuggestions?limit={limit}&cursor={cursor}"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def search_actors(self, q: str, limit: int | None = None, cursor: str = "") -> dict:
        """Search for actors."""
        if limit is None:
            limit = LIMIT

        endpoint = f"{self.pds_host}/xrpc/app.bsky.actor.searchActors?q={q}&limit={limit}&cursor={cursor}"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def get_actor_likes(self, actor: str, limit: int | None = None, cursor: str = "") -> dict:  # Requires Auth
        """Get a given actors likes."""
        if limit is None:
            limit = LIMIT

        endpoint = f"{self.pds_host}/xrpc/app.bsky.feed.getActorLikes?actor={actor}&limit={limit}&cursor={cursor}"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def get_author_feed(self, actor: str, limit: int | None = None) -> dict:
        """Get a specific user feed."""
        if limit is None:
            limit = LIMIT

        endpoint = f"{self.pds_host}/xrpc/app.bsky.feed.getAuthorFeed?actor={actor}&limit={limit}"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def get_feed(self, feed: str, limit: int | None = None, cursor: str = "") -> dict:
        """Get a specified feed."""
        if limit is None:
            limit = LIMIT

        endpoint = f"{self.pds_host}/xrpc/app.bsky.feed.getFeed?feed={feed}&limit={limit}&cursor={cursor}"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def get_suggested_feeds(self, limit: int | None = None, cursor: str = "") -> dict:
        """Get suggested feeds."""
        if limit is None:
            limit = LIMIT

        endpoint = f"{self.pds_host}/xrpc/app.bsky.feed.getSuggestedFeeds?limit={limit}&cursor={cursor}"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def get_timeline(self) -> dict:
        """Get a users timeline."""
        endpoint = f"{self.pds_host}/xrpc/app.bsky.feed.getTimeline"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    # Only function that needs this many params, I am not making a data class for it
    async def search_posts(  # noqa: PLR0913
        self,
        q: str,
        sort: Literal["top", "latest"] = "latest",
        since: str = "",
        until: str = "",
        mentions: str = "",
        author: str = "",
        tag: str = "",
        limit: int | None = None,
        cursor: str = "",
    ) -> dict:
        """Search for bluesky posts.

        Args:
            q (str): the given query
            sort (Literal[&quot;top&quot;, &quot;latest&quot;], optional): The sort Order. Defaults to "latest".
            since (str, optional): Since when in YYYY-MM-DD format. Defaults to "".
            until (str, optional): Until when in YYYY-MM-DD format. Defaults to "".
            mentions (str, optional): Post mentions the given account. Defaults to "".
            author (str, optional): Author of a given post. Defaults to "".
            tag (str, optional): Tags on the post. Defaults to "".
            limit (int, optional): Limit the number returned. Defaults to LIMIT.
            cursor (str, optional): Bsky Cursor. Defaults to "".

        """
        if limit is None:
            limit = LIMIT

        endpoint = (
            f"{self.pds_host}/xrpc/app.bsky.feed.searchPosts"
            f"?q={q}&sort={sort}&since={since}&until={until}"
            f"&mentions={mentions}&author={author}&tag={tag}"
            f"&limit={limit}&cursor={cursor}"
        )
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def get_followers(self, actor: str, limit: int | None = None, cursor: str = "") -> dict:
        """Get a users followers."""
        if limit is None:
            limit = LIMIT

        endpoint = f"{self.pds_host}/xrpc/app.bsky.graph.getFollowers?actor={actor}&limit={limit}&cursor={cursor}"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def get_follows(self, actor: str, limit: int | None = None, cursor: str = "") -> dict:
        """Get a users follows."""
        if limit is None:
            limit = LIMIT

        endpoint = f"{self.pds_host}/xrpc/app.bsky.graph.getFollows?actor={actor}&limit={limit}&cursor={cursor}"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def get_mutual_follows(self, actor: str, limit: int | None = None, cursor: str = "") -> dict:
        """Get a users mutual follows."""
        if limit is None:
            limit = LIMIT

        endpoint = f"{self.pds_host}/xrpc/app.bsky.graph.getKnownFollowers?actor={actor}&limit={limit}&cursor={cursor}"
        response = await self.client.get(
            endpoint,
        )
        return await response.json()

    async def get_blob(self, url: str) -> str:
        """Get a specific blob."""
        did, cid = url.split("/")[-2:]
        cid = cid.split("@")[0]
        return f"https://bsky.social/xrpc/com.atproto.sync.getBlob?did={did}&cid={cid}"
