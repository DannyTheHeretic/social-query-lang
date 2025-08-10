# Imports
import requests  # The system we will actually use



class Session:
    """Class to etablish an auth session"""
    def __init__(self, username: str, password: str):
        #Bluesky credentials
        self.username = username
        self.password = password
        self.pds_host = "https://bsky.social"
        #Instance client
        #Access token
        self.access_jwt = None
        #Refresh token
        self.refresh_jwt = None

    def login(self):
        """Create an authenticated session and save tokens."""
        endpoint = f"{self.pds_host}/xrpc/com.atproto.server.createSession"
        session_info = requests.post(
                endpoint,
                headers={"Content-Type": "application/json"},
                json = {
                    "identifier":self.username,
                    "password":self.password,
                },
                timeout=30,
            ).json()
        self.access_jwt = session_info["accessJwt"]
        self.refresh_jwt = session_info["refreshJwt"]
        print("Connexion réussie.")
        print("Access token :", self.access_jwt)
        print("Refresh token :", self.refresh_jwt)

    def get_profile(self):
        """Example : get user profile"""
        endpoint = f"{self.pds_host}/xrpc/app.bsky.actor.getProfile?actor={self.username}"
        return requests.get(
            endpoint,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.access_jwt}"},
            timeout=30,
        ).json()


if __name__ == "__main__":
    USERNAME = "Nothing_AHAHA"
    PASSWORD = "You thought i'll write the password here you fool"

    session = Session(USERNAME, PASSWORD)
    session.login()

    profile = session.get_profile()

    print(profile)
