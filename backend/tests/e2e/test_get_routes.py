def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Adaptive Learning Platform API is running!",
        "status": "ok",
        "environment": "development",
    }


def test_get_learning_tracks(client):
    response = client.get("/learning_tracks")
    assert response.status_code == 200
    # assert isinstance(response.json(), list)
    assert len(response.json()) == 3


def test_get_questions_unauthenticated(client):
    track_id = 1
    response = client.get(f"/questions/{track_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 15


def test_get_questions_authenticated():
    # This test requires a valid JWT token for an authenticated user.
    pass
    

