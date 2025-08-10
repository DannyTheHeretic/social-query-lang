# Imports
from atproto import Client


class Session:
    """Class to etablish an auth session"""
    def __init__(self, username: str, password: str):
        #Bluesky credentials
        self.username = username
        self.password = password
        #Instance client
        self.client = Client()
        #Access token
        self.access_jwt = None
        #Refresh token
        self.refresh_jwt = None

    def login(self):
        """Create an authenticated session and save tokens."""
        session_info = self.client.login(self.username, self.password)
        self.access_jwt = session_info.accessJwt
        self.refresh_jwt = session_info.refreshJwt
        print("Connexion réussie.")
        print("Access token :", self.access_jwt)
        print("Refresh token :", self.refresh_jwt)

    def get_profile(self):
        """Example : get user profile"""
        profile = self.client.app.bsky.actor.get_profile({'actor': self.username})
        return profile


if __name__ == "__main__":
    USERNAME = "Nothing_AHAHA"
    PASSWORD = "You tought i'll write the password here you fool"

    session = Session(USERNAME, PASSWORD)
    session.login()

    profile = session.get_profile()
    print("Nom affiché :", profile.displayName)
