def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Adaptive Learning Platform API is running!",
        "status": "ok",
        "environment": "development",
    }


def test_create_submission(client, auth_headers):
    response = client.post(
        "/submissions",
        headers=auth_headers,
        json={
            "question_id": 1,
            "answer": 2,
            "track_id": 1
        }
    )

    assert response.status_code == 200
    submission_response = response.json()
    assert "submission" in submission_response
    assert "updated_skill_profile" in submission_response