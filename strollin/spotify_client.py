import os
import json
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

MAPPINGS_FILE = os.path.join(os.path.dirname(__file__), 'mappings.json')


class SpotifyClient:
    def __init__(self):
        client_id = os.getenv('SPOTIPY_CLIENT_ID')
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
        scope = 'user-modify-playback-state user-read-playback-state'

        if not client_id or not client_secret or not redirect_uri:
            raise RuntimeError('Set SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET and SPOTIPY_REDIRECT_URI in .env')

        self.oauth = SpotifyOAuth(client_id=client_id,
                                  client_secret=client_secret,
                                  redirect_uri=redirect_uri,
                                  scope=scope,
                                  open_browser=True)
        token_info = self.oauth.get_cached_token()
        if not token_info:
            # This will open a browser to authenticate the first time
            auth_url = self.oauth.get_authorize_url()
            print('Please navigate here to authorize the app:', auth_url)
            code = input('Enter the URL you were redirected to after approval: ').strip()
            token_info = self.oauth.parse_response_code(code)
            # token_info retrieval simplified; Spotipy handles this flow when using prompt_for_user_token

        token = self.oauth.get_access_token(as_dict=False)
        self.sp = spotipy.Spotify(auth=token)

        # load mappings
        try:
            with open(MAPPINGS_FILE, 'r') as f:
                self.mappings = json.load(f)
        except Exception:
            # default empty mapping
            self.mappings = {}

    def play_for(self, name):
        """Play a mapped Spotify URI for the given person name.
        The mapping file should be a JSON object: { "Alice": "spotify:track:..." }
        """
        uri = self.mappings.get(name)
        if not uri:
            print(f'No mapping found for {name}; skipping playback')
            return
        try:
            # Try to start playback
            if uri.startswith('spotify:track:'):
                self.sp.start_playback(uris=[uri])
            else:
                # playlist/album/uri
                self.sp.start_playback(context_uri=uri)
            print(f'Started playback for {name}: {uri}')
        except spotipy.SpotifyException as e:
            print('Spotify API error:', e)
