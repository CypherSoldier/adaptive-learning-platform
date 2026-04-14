from fastapi import FastAPI
from .routes.submission_routes import router as submission_router
from .routes.question_routes import router as question_router
from .routes.auth_routes import router as auth_router
from .routes.user_routes import router as skill_profile_router
from .routes.track_routes import router as learning_track_router


def register_routes(app: FastAPI):
    app.include_router(submission_router)
    app.include_router(auth_router)
    app.include_router(question_router)
    app.include_router(skill_profile_router)
    app.include_router(learning_track_router)
