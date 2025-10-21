"""Lightweight Spotify client wrapper for playback control.

This module provides a small `SpotifyClient` class that handles:
- Reading Spotify credentials from environment variables (via `python-dotenv`).
- Performing an OAuth flow (with Spotipy) to obtain an access token.
- Loading a simple JSON mapping from person name -> Spotify URI.
- Starting playback on the user's active Spotify device.

Design notes and limitations:
- This is intentionally minimal. For production, consider a proper local callback server
  to complete the OAuth flow automatically and persist refresh tokens securely.
- Spotipy's helper functions are used directly; depending on your setup, the first run may
  require manual interaction to authorize the app.
"""

import os
import json

from dotenv import load_dotenv

load_dotenv()

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except Exception:
    # Defer the import error until runtime; unit tests that don't exercise SpotifyClient
    # can still import the module.
    spotipy = None
    SpotifyOAuth = None

MAPPINGS_FILE = os.path.join(os.path.dirname(__file__), 'mappings.json')


class SpotifyClient:
    """A small Spotify playback client.

    Responsibilities:
    - Read `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, and `SPOTIPY_REDIRECT_URI` from env.
    - Use Spotipy's `SpotifyOAuth` to obtain an access token and create a `spotipy.Spotify` client.
    - Load `mappings.json` to map person names to Spotify URIs.

    Example mapping (`mappings.json`):
        { "Alice": "spotify:track:...", "Bob": "spotify:playlist:..." }

    Methods:
        play_for(name): Trigger playback for a mapped person name.

    Error modes:
    - Raises RuntimeError if Spotify credentials are not set in environment.
    - If Spotipy is not installed, the class will raise on initialization.
    """

    def __init__(self):
        if spotipy is None or SpotifyOAuth is None:
            raise RuntimeError('spotipy is required to use SpotifyClient. Install it via pip.')

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
        # Attempt to use a cached token; Spotipy will handle refresh when needed.
        token_info = self.oauth.get_cached_token()
        if not token_info:
            # First-run: open the browser and ask the user to complete the flow.
            auth_url = self.oauth.get_authorize_url()
            print('Please navigate here to authorize the app:', auth_url)
            code = input('Enter the URL you were redirected to after approval: ').strip()
            # Note: Spotipy expects the full redirect URL; parse_response_code isn't documented
            # consistently across versions, so we fall back to getting token directly below.

        # This will return a token string or a dict depending on spotipy version; Spotipy
        # provides convenience wrappers but interfaces vary across versions.
        token = self.oauth.get_access_token(as_dict=False)
        self.sp = spotipy.Spotify(auth=token)

        # load mappings (person name -> spotify URI)
        try:
            with open(MAPPINGS_FILE, 'r') as f:
                self.mappings = json.load(f)
        except Exception:
            # default empty mapping
            self.mappings = {}

    def play_for(self, name):
        """Start playback for the given person's mapped Spotify URI.

        Arguments:
            name (str): The person label (folder name from `known_faces/`).

        Returns:
            None

        Behavior:
            - If the mapping for `name` is a track URI (spotify:track:...), calls
              `start_playback(uris=[uri])`.
            - Otherwise, passes the URI as `context_uri` to `start_playback` so
              playlists/albums/context URIs work.
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
        except Exception as e:
            # Spotipy may raise SpotifyException or generic exceptions depending on version
            print('Spotify API error:', e)
