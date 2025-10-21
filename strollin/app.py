import os
import time
from dotenv import load_dotenv
import cv2
from faces import load_known_faces, recognize_faces
from spotify_client import SpotifyClient

load_dotenv()

KNOWN_DIR = os.getenv("KNOWN_FACES_DIR", "known_faces")
COOLDOWN_SECONDS = 10


def main():
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
                        # SpotifyClient will map name -> track/playlist from mappings.json or internal mapping
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
