import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import register_routes
from .logging import configure_logging, LogLevels

configure_logging(LogLevels.info)


app = FastAPI(
    title="Adaptive Learning Platform",
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