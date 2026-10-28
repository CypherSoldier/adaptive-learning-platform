from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.sql import func
from src.database.session import Base


class UserQuestionProgress(Base):
    __tablename__ = "user_question_progress"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_user_question_progress_user_question"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    completed = Column(Boolean, nullable=False, default=False, server_default="0")
    completed_at = Column(DateTime(timezone=True))
    is_seeded = Column(Boolean, nullable=False, default=False, server_default="0")


class TrackOnboarding(Base):
    __tablename__ = "track_onboarding"
    __table_args__ = (UniqueConstraint("user_id", "track_id", name="uq_track_onboarding_user_track"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"), nullable=False)
    completed = Column(Boolean, nullable=False, default=False, server_default="0")


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(String(36), primary_key=True)
    idempotency_key = Column(String(255), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"), nullable=False)
    session_type = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class LearningSessionQuestion(Base):
    __tablename__ = "learning_session_questions"
    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uq_session_question"),
        UniqueConstraint("session_id", "position", name="uq_session_position"),
    )

    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), ForeignKey("learning_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    position = Column(Integer, nullable=False)
