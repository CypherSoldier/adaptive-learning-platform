from sqlalchemy import Column, ForeignKey, Integer, JSON, String
from src.database.session import Base


class AIGenerationRequest(Base):
    """Persist generated question IDs so retries of one session are idempotent."""

    __tablename__ = "ai_generation_requests"

    request_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"), nullable=False)
    question_ids = Column(JSON, nullable=False)
