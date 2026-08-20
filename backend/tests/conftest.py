import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.session import Base, get_db
from src.models import (
    User,
    LearningTrack,
    Question,
    Topic,
    Submission,
    UserSkillProfile,
)
from src.rate_limiter import limiter
from src.seed_initial_data import seed_tracks, seed_questions
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def db_session(tmp_path):
    database_path = tmp_path / "test.db"
    sql_url = f"sqlite:///{database_path}"
    engine = create_engine(sql_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Seed test database with initial data
        seed_tracks(db)
        seed_questions(db)
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    from src.main import app

    limiter.reset()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client):
    response = client.post(
        "/auth/",
        json={
            "email": "test.user@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201

    response = client.post(
        "/auth/token",
        data={
            "username": "test.user@example.com",
            "password": "testpassword123",
            "grant_type": "password",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
