# API Documentation — Face-Spotify

This file contains extracted docstrings from the main modules to serve as a quick reference.

## app.py

Main runner for the Face-Spotify prototype.

This module ties together webcam-based face recognition and Spotify playback.

Typical flow:
- Load known face encodings from `known_faces/` (or path set by `KNOWN_FACES_DIR`).
- Initialize a `SpotifyClient` (handles OAuth and playback).
- Capture frames from the default webcam and run face recognition.
- When a known face is found, map the person's name to a Spotify URI and start playback.

Notes:
- This is a minimal prototype. Improve error handling and UX for production use.
- Requires `face_recognition` and `opencv-python` at runtime. These imports are done lazily
  in `faces.py` to allow tests to import modules without native deps installed.

### main()

Start the webcam loop and trigger Spotify playback when known faces are seen.

Behavior:
- Loads known faces from `KNOWN_DIR` (default: `known_faces/`).
- Initializes `SpotifyClient` (will prompt for OAuth if not authorized).
- Captures frames from the default camera (index 0).
- If one or more known faces are visible, calls `SpotifyClient.play_for(name)`.

Returns:
- None

Error modes:
- If the webcam cannot be opened, prints a message and returns.
- If Spotify credentials are missing/misconfigured, `SpotifyClient` will raise.

Example:

    python app.py


## faces.py

Face utilities for loading known faces and recognizing people in frames.

This module intentionally defers heavy imports (dlib/face_recognition/opencv) until
functions are called so lightweight tests can import the module without native deps.

Functions
- load_known_faces(known_dir="known_faces") -> (encodings, names)
- recognize_faces(frame, known_encodings, known_names, tolerance=0.5) -> [names]

Usage example:

    encs, names = load_known_faces('known_faces')
    recognized = recognize_faces(frame, encs, names)

### load_known_faces(known_dir='known_faces')

Load and return face encodings and labels from a folder structure.

The expected layout is:

    known_faces/
        Alice/
            img1.jpg
        Bob/
            img1.jpg

Args:
- known_dir (str): Path to the folder containing subfolders for each person.

Returns:
- tuple: (encodings, names)
    - encodings (list): List of 128-d face encodings (one per image that had a face).
    - names (list): Parallel list of names (folder names) for each encoding.

Raises:
- RuntimeError: If `face_recognition` is not installed.

### recognize_faces(frame, known_encodings, known_names, tolerance=0.5)

Recognize known faces in a single BGR frame.

Args:
- frame (numpy.ndarray): BGR image as returned by OpenCV `VideoCapture.read()`.
- known_encodings (list): List of known face encodings.
- known_names (list): List of names matching `known_encodings`.
- tolerance (float): Distance threshold for `face_recognition.compare_faces`.

Returns:
- list: Names of recognized people found in the frame. May be empty.

Raises:
- RuntimeError: If `cv2` or `face_recognition` are not installed.


## spotify_client.py

Lightweight Spotify client wrapper for playback control.

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

### SpotifyClient

A small Spotify playback client.

Responsibilities:
- Read `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, and `SPOTIPY_REDIRECT_URI` from env.
- Use Spotipy's `SpotifyOAuth` to obtain an access token and create a `spotipy.Spotify` client.
- Load `mappings.json` to map person names to Spotify URIs.

Example mapping (`mappings.json`):

    { "Alice": "spotify:track:...", "Bob": "spotify:playlist:..." }

Methods:
- play_for(name): Trigger playback for a mapped person name.

Error modes:
- Raises RuntimeError if Spotify credentials are not set in environment.
- If Spotipy is not installed, the class will raise on initialization.

### play_for(name)

Start playback for the given person's mapped Spotify URI.

Arguments:
- name (str): The person label (folder name from `known_faces/`).

Returns:
- None

Behavior:
- If the mapping for `name` is a track URI (spotify:track:...), calls
  `start_playback(uris=[uri])`.
- Otherwise, passes the URI as `context_uri` to `start_playback` so
  playlists/albums/context URIs work.
