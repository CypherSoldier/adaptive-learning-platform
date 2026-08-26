import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import register_routes
from .logging import configure_logging, LogLevels
from .seed_initial_data import seed_questions, seed_tracks
from .database.session import SessionLocal
configure_logging(LogLevels.info)
# remove line 9 for railway
from .database.session import engine, Base

# remove below for railway
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Adaptive Learning Platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://adaptive-learning-platform-sand.vercel.app"],
    #allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_seed_data():
    """Seed database with initial data on app startup"""
    db = SessionLocal()
    try:
        seed_tracks(db) # remove for railway
        seed_questions(db)
    finally:
        db.close()


@app.get("/")
async def root():
    return {
        "message": "Adaptive Learning Platform API is running!",
        "status": "ok",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development")
    }

register_routes(app)