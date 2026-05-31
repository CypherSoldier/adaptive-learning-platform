from fastapi import FastAPI
from .database.session import engine, Base
from .api import register_routes
from .logging import configure_logging, LogLevels
from .models.learning_track import LearningTrack
from .models.topic import Topic
from .models.question import Question
from .models.submission import Submission
from .models.user import User
from .models.user_skill_profile import UserSkillProfile
from fastapi.middleware.cors import CORSMiddleware

configure_logging(LogLevels.info)

app = FastAPI(title="Monolith Example")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://adaptive-learning-platform-sand.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""" Only uncomment below to create new tables, 
otherwise the tests will fail if not connected
"""
Base.metadata.create_all(bind=engine)

register_routes(app)
