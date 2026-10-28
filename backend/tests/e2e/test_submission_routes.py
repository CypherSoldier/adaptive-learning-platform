def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Adaptive Learning Platform API is running!",
        "status": "ok",
        "environment": "development",
    }


def test_create_submission(client, auth_headers):
    session_response = client.post(
        "/sessions/1",
        headers={**auth_headers, "Idempotency-Key": "submission-route-test"},
    )
    assert session_response.status_code == 200
    session = session_response.json()
    question = session["questions"][0]

    response = client.post(
        "/submissions",
        headers=auth_headers,
        json={
            "question_id": question["id"],
            "answer": question["correct_answer"],
            "track_id": 1,
            "session_id": session["session_id"],
        }
    )

    assert response.status_code == 200
    submission_response = response.json()
    assert "submission" in submission_response
    assert "updated_skill_profile" in submission_response
