import os
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Local relative imports
from .database.session import engine, Base
from .api import register_routes
from .logging import configure_logging, LogLevels
from .models.learning_track import LearningTrack
from .models.topic import Topic
from .models.question import Question
from .models.submission import Submission
from .models.user import User
from .models.user_skill_profile import UserSkillProfile
from seed_initial_data import seed_questions, seed_tracks 

configure_logging(LogLevels.info)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    if os.getenv("RUN_SEED", "false").lower() == "true":
        print("🚀 Running initial data seeding...")
        seed_tracks()
        seed_questions()
        print("Initial seeding completed.")

    yield

    print("Application shutting down...")


app = FastAPI(
    title="Adaptive Learning Platform",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://adaptive-learning-platform-sand.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Adaptive Learning Platform API is running!",
        "status": "ok",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development")
    }

register_routes(app)