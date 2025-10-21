# Face-Spotify

A minimal Python starter project that detects/identifies faces from a webcam and triggers Spotify playback for recognized users.

This scaffold provides:
- `app.py` — main runner that connects face recognition and Spotify playback
- `faces.py` — utilities to load known faces and recognize people from camera frames
- `spotify_client.py` — small wrapper around Spotipy to authenticate and start playback
- `requirements.txt` — minimal dependencies
- `.env.example` — environment variables you must set
- `mappings.json` — example mapping of person name -> Spotify track URI
- `tests/test_smoke.py` — smoke test to verify imports

Quick setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a Spotify Developer App at https://developer.spotify.com/dashboard and set a Redirect URI (e.g. `http://localhost:8888/callback`).

3. Copy `.env.example` to `.env` and fill in `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, and `SPOTIPY_REDIRECT_URI`.

4. Add some labeled images into `known_faces/Name/` (one or more images per person). Filenames don't matter; each folder name becomes the person label.

5. Run the app:

```bash
python app.py
```

Notes

- Spotify playback requires an active device (Spotify client on desktop/mobile or a Spotify Connect device).
- This is a starter scaffold. You should improve error handling, add persistent storage, and secure secrets for production.
