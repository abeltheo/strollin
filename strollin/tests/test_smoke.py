def test_imports():
    # Ensure project root is on sys.path when running under pytest
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    import faces
    import spotify_client

    assert hasattr(faces, 'load_known_faces')
    assert hasattr(spotify_client, 'SpotifyClient')
