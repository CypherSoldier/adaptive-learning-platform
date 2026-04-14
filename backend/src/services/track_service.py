from sqlalchemy.orm import Session
from src.models.learning_track import LearningTrack

def list_tracks(db: Session):
    return db.query(LearningTrack).all()

def assign_track(user_level: str):
    if user_level == "beginner":
        return "basics"
    return "advanced"