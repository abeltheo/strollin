"""Main runner for the Face-Spotify prototype.

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
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

from faces import load_known_faces, recognize_faces
from spotify_client import SpotifyClient

KNOWN_DIR = os.getenv("KNOWN_FACES_DIR", "known_faces")
COOLDOWN_SECONDS = 10


def main():
    """Start the webcam loop and trigger Spotify playback when known faces are seen.

    Behavior:
    - Loads known faces from `KNOWN_DIR` (default: `known_faces/`).
    - Initializes `SpotifyClient` (will prompt for OAuth if not authorized).
    - Captures frames from the default camera (index 0).
    - If one or more known faces are visible, calls `SpotifyClient.play_for(name)`.

    Returns:
        None

    Error modes:
    - If the webcam cannot be opened, prints a message and returns.
    - If Spotify credentials are missing/misconfigured, `SpotifyClient` will raise.

    Example:
        python app.py
    """

    try:
        import cv2
    except Exception:
        raise RuntimeError("opencv-python is required to run the main app. Install with pip.")

    print("Loading known faces...")
    known_encodings, known_names = load_known_faces(KNOWN_DIR)
    print(f"Loaded {len(known_names)} known people: {known_names}")

    spotify = SpotifyClient()

    last_seen = {}

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam. Exiting.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            names = recognize_faces(frame, known_encodings, known_names)
            if names:
                for name in names:
                    now = time.time()
                    if name not in last_seen or (now - last_seen[name]) > COOLDOWN_SECONDS:
                        print(f"Recognized: {name}; triggering Spotify playback")
                        # SpotifyClient maps name -> track/playlist from mappings.json
                        spotify.play_for(name)
                        last_seen[name] = now

            # show the frame (optional)
            cv2.imshow('Face-Spotify', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
