"""Face utilities for loading known faces and recognizing people in frames.

This module intentionally defers heavy imports (dlib/face_recognition/opencv) until
functions are called so lightweight tests can import the module without native deps.

Functions
- load_known_faces(known_dir="known_faces") -> (encodings, names)
- recognize_faces(frame, known_encodings, known_names, tolerance=0.5) -> [names]

Usage example:
    encs, names = load_known_faces('known_faces')
    recognized = recognize_faces(frame, encs, names)
"""

import os


def load_known_faces(known_dir='known_faces'):
    """Load and return face encodings and labels from a folder structure.

    The expected layout is:

        known_faces/
            Alice/
                img1.jpg
            Bob/
                img1.jpg

    Args:
        known_dir (str): Path to the folder containing subfolders for each person.

    Returns:
        tuple: (encodings, names)
            encodings (list): List of 128-d face encodings (one per image that had a face).
            names (list): Parallel list of names (folder names) for each encoding.

    Raises:
        RuntimeError: If `face_recognition` is not installed.
    """
    try:
        import face_recognition
    except Exception as e:
        raise RuntimeError("face_recognition is required to load known faces. Install it via pip.") from e

    encodings = []
    names = []
    if not os.path.isdir(known_dir):
        return encodings, names

    for person_name in os.listdir(known_dir):
        person_dir = os.path.join(known_dir, person_name)
        if not os.path.isdir(person_dir):
            continue
        for fname in os.listdir(person_dir):
            path = os.path.join(person_dir, fname)
            try:
                image = face_recognition.load_image_file(path)
                face_encs = face_recognition.face_encodings(image)
                if face_encs:
                    encodings.append(face_encs[0])
                    names.append(person_name)
            except Exception:
                # ignore files that fail to load/encode
                continue
    return encodings, names


def recognize_faces(frame, known_encodings, known_names, tolerance=0.5):
    """Recognize known faces in a single BGR frame.

    Args:
        frame (numpy.ndarray): BGR image as returned by OpenCV `VideoCapture.read()`.
        known_encodings (list): List of known face encodings.
        known_names (list): List of names matching `known_encodings`.
        tolerance (float): Distance threshold for `face_recognition.compare_faces`.

    Returns:
        list: Names of recognized people found in the frame. May be empty.

    Raises:
        RuntimeError: If `cv2` or `face_recognition` are not installed.
    """
    if not known_encodings:
        return []
    try:
        import cv2
        import face_recognition
    except Exception as e:
        raise RuntimeError("cv2 and face_recognition are required to recognize faces. Install them via pip.") from e

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb)
    encs = face_recognition.face_encodings(rgb, locations)
    results = []
    for enc in encs:
        matches = face_recognition.compare_faces(known_encodings, enc, tolerance=tolerance)
        if True in matches:
            first_match_index = matches.index(True)
            results.append(known_names[first_match_index])
    return results
