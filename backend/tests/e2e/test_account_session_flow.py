from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api import register_routes
from src.database.session import get_db
from src.models.user import User
from src.models.user_question_progress import UserQuestionProgress
from src.models.user_skill_profile import UserSkillProfile
from src.services import auth_service, session_service


def _register_and_login(client: TestClient, email: str, full_name: str, password: str):
    created = client.post("/auth/", json={"email": email, "full_name": full_name, "password": password})
    assert created.status_code == 201
    response = client.post("/auth/token", data={"username": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_account_switch_onboarding_progress_and_next_session_e2e(db_session: Session, monkeypatch):
    app = FastAPI()
    register_routes(app)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    generated_batch = 0

    def fake_generate(topic: str, difficulty: int, count: int):
        nonlocal generated_batch
        generated_batch += 1
        return [
            {
                "question": f"E2E generated batch {generated_batch} item {index} for {topic}",
                "options": ["Correct", "Wrong A", "Wrong B", "Wrong C"],
                "correct_answer": 0,
                "explanation": "The first option is correct.",
                "difficulty": difficulty,
            }
            for index in range(count)
        ]

    monkeypatch.setattr(session_service, "generate_mcq", fake_generate)
    monkeypatch.setattr(
        auth_service,
        "verify_firebase_id_token",
        lambda _token: {"email": "first@example.com", "name": "First Learner"},
    )

    with TestClient(app) as client:
        # The email/password account is created first, then Google login resolves
        # to that same backend identity and returns the ID needed by the frontend.
        password_headers = _register_and_login(client, "first@example.com", "First Learner", "password123")
        password_identity = client.get("/users/me", headers=password_headers).json()
        google_login = client.post("/auth/google", json={"token": "fake-firebase-token"})
        assert google_login.status_code == 200
        google_identity = google_login.json()["user"]
        assert google_identity["user_id"] > 0
        assert google_identity["user_id"] == password_identity["user_id"]
        first_headers = {"Authorization": f"Bearer {google_login.json()['access_token']}"}
        assert db_session.query(User).filter_by(email="first@example.com").count() == 1

        # A new JavaScript track starts with exactly its 15 seeded questions.
        first_session = client.post(
            "/sessions/3", headers={**first_headers, "Idempotency-Key": "first-js-onboarding"}
        )
        assert first_session.status_code == 200
        onboarding = first_session.json()
        assert onboarding["session_type"] == "onboarding"
        assert len(onboarding["questions"]) == 15

        # Retrying the same key returns the identical persisted session and order.
        retry = client.post(
            "/sessions/3", headers={**first_headers, "Idempotency-Key": "first-js-onboarding"}
        )
        assert retry.status_code == 200
        assert retry.json()["session_id"] == onboarding["session_id"]
        assert [q["id"] for q in retry.json()["questions"]] == [q["id"] for q in onboarding["questions"]]

        first_seeded_question = onboarding["questions"][0]
        wrong_answer = (first_seeded_question["correct_answer"] + 1) % len(first_seeded_question["options"])
        first_submission = client.post(
            "/submissions",
            headers=first_headers,
            json={"question_id": first_seeded_question["id"], "answer": wrong_answer,
                  "track_id": 3, "session_id": onboarding["session_id"]},
        )
        assert first_submission.status_code == 200
        assert first_submission.json()["submission"]["is_correct"] is False

        # Starting another onboarding session resumes only unassessed seeded
        # questions. A wrong answer is not repeated, and still informs the profile.
        remaining_onboarding_response = client.post(
            "/sessions/3", headers={**first_headers, "Idempotency-Key": "first-js-onboarding-remaining"}
        )
        assert remaining_onboarding_response.status_code == 200
        remaining_onboarding = remaining_onboarding_response.json()
        assert remaining_onboarding["session_type"] == "onboarding"
        assert len(remaining_onboarding["questions"]) == 14
        assert first_seeded_question["id"] not in {q["id"] for q in remaining_onboarding["questions"]}

        for question in remaining_onboarding["questions"]:
            submitted = client.post(
                "/submissions",
                headers=first_headers,
                json={"question_id": question["id"], "answer": question["correct_answer"],
                      "track_id": 3, "session_id": remaining_onboarding["session_id"]},
            )
            assert submitted.status_code == 200
            assert submitted.json()["submission"]["is_correct"] is True

        # Progress belongs to the authenticated user; no user_id query parameter is needed.
        progress = client.get("/users/skill-profiles", headers=first_headers)
        assert progress.status_code == 200
        assert [profile["track_id"] for profile in progress.json()] == [3]
        assert progress.json()[0]["attempts"] == 15

        # Even though the first answer was wrong, all 15 assessment questions
        # have been submitted, so the next session uses AI questions.

        # A fresh key transitions the completed track to a 10-question AI session.
        ai_response = client.post(
            "/sessions/3", headers={**first_headers, "Idempotency-Key": "first-js-ai"}
        )
        assert ai_response.status_code == 200
        ai_session = ai_response.json()
        assert ai_session["session_type"] == "ai"
        assert len(ai_session["questions"]) == 10
        assert all(q["source"] == "ai_generated" for q in ai_session["questions"])

        for question in ai_session["questions"]:
            submitted = client.post(
                "/submissions",
                headers=first_headers,
                json={"question_id": question["id"], "answer": question["correct_answer"],
                      "track_id": 3, "session_id": ai_session["session_id"]},
            )
            assert submitted.status_code == 200

        next_ai_response = client.post(
            "/sessions/3", headers={**first_headers, "Idempotency-Key": "first-js-ai-next"}
        )
        assert next_ai_response.status_code == 200
        assert len(next_ai_response.json()["questions"]) == 10
        assert set(q["id"] for q in next_ai_response.json()["questions"]).isdisjoint(
            q["id"] for q in ai_session["questions"]
        )

        # Switching tracks starts an independent seeded onboarding session.
        cpp_response = client.post(
            "/sessions/2", headers={**first_headers, "Idempotency-Key": "first-cpp-onboarding"}
        )
        assert cpp_response.status_code == 200
        cpp_session = cpp_response.json()
        assert cpp_session["session_type"] == "onboarding"
        assert len(cpp_session["questions"]) == 15
        for question in cpp_session["questions"]:
            submitted = client.post(
                "/submissions", headers=first_headers,
                json={"question_id": question["id"], "answer": question["correct_answer"],
                      "track_id": 2, "session_id": cpp_session["session_id"]},
            )
            assert submitted.status_code == 200
        first_progress_by_track = client.get("/users/skill-profiles", headers=first_headers)
        assert {profile["track_id"] for profile in first_progress_by_track.json()} == {2, 3}

        # A second account cannot reuse the first account's key, gets its own
        # seeded assignment, and cannot complete the first account's progress.
        second_headers = _register_and_login(client, "second@example.com", "Second Learner", "password456")
        collision = client.post(
            "/sessions/3", headers={**second_headers, "Idempotency-Key": "first-js-onboarding"}
        )
        assert collision.status_code == 409
        second_session_response = client.post(
            "/sessions/3", headers={**second_headers, "Idempotency-Key": "second-js-onboarding"}
        )
        assert second_session_response.status_code == 200
        second_session = second_session_response.json()
        assert len(second_session["questions"]) == 15
        shared_question_id = onboarding["questions"][0]["id"]
        wrong_answer = (onboarding["questions"][0]["correct_answer"] + 1) % len(onboarding["questions"][0]["options"])
        wrong = client.post(
            "/submissions", headers=second_headers,
            json={"question_id": shared_question_id, "answer": wrong_answer,
                  "track_id": 3, "session_id": second_session["session_id"]},
        )
        assert wrong.status_code == 200
        assert wrong.json()["submission"]["is_correct"] is False
        first_progress = db_session.query(UserQuestionProgress).filter_by(
            user_id=google_identity["user_id"], question_id=shared_question_id
        ).one()
        second_user_id = int(client.get("/users/me", headers=second_headers).json()["user_id"])
        second_progress = db_session.query(UserQuestionProgress).filter_by(
            user_id=second_user_id, question_id=shared_question_id
        ).one()
        assert first_progress.completed is False
        assert second_progress.completed is False

        python_response = client.post(
            "/sessions/1", headers={**second_headers, "Idempotency-Key": "second-python-onboarding"}
        )
        assert python_response.status_code == 200
        assert python_response.json()["session_type"] == "onboarding"
        assert len(python_response.json()["questions"]) == 15

        # The unique user/track constraint and get-or-create path prevent the
        # duplicate profiles observed in the original manual flow.
        assert db_session.query(UserSkillProfile).filter_by(user_id=google_identity["user_id"], track_id=3).count() == 1

        invalid_track = client.get("/questions/0")
        assert invalid_track.status_code == 404
