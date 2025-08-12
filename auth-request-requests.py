# Imports
import requests  # The system we will actually use


class Session:
    """Class to etablish an auth session."""

    def __init__(self, username: str, password: str) -> None:
        # Bluesky credentials
        self.username = username
        self.password = password
        self.pds_host = "https://bsky.social"
        # Instance client
        self.client = requests.Session()
        # Access token
        self.access_jwt = None
        # Refresh token
        self.refresh_jwt = None

    def login(self) -> None:
        """Create an authenticated session and save tokens."""
        endpoint = f"{self.pds_host}/xrpc/com.atproto.server.createSession"
        session_info = self.client.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            json={
                "identifier": self.username,
                "password": self.password,
            },
            timeout=30,
        ).json()
        self.access_jwt = session_info["accessJwt"]
        self.refresh_jwt = session_info["refreshJwt"]
        self.client.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_jwt}",
            },
        )

        print("Connexion réussie.")
        print("Access token :", self.access_jwt)
        print("Refresh token :", self.refresh_jwt)

    def get_profile(self) -> dict:
        """Get a user profile."""
        endpoint = f"{self.pds_host}/xrpc/app.bsky.actor.getProfile?actor={self.username}"
        return self.client.get(
            endpoint,
        ).json()

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


if __name__ == "__main__":
    USERNAME = "Nothing_AHAHA"
    PASSWORD = "You tought i'll write the password here you fool"  # noqa: S105

    session = Session(USERNAME, PASSWORD)
    session.login()

    profile = session.get_profile()

    print(profile)

    search = session.get_actor_feeds("tess.bsky.social")
    print(search)
