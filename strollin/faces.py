import os


def load_known_faces(known_dir='known_faces'):
    """Load known face encodings from subfolders in `known_dir`.
    Each subfolder name is treated as the person's label.
    Returns (encodings_list, names_list)
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
    """Given a BGR frame (cv2), return list of recognized names found in the frame."""
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
