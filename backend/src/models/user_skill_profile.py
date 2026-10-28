from sqlalchemy import Column, Integer, ForeignKey, Float, UniqueConstraint
from src.database.session import Base


class UserSkillProfile(Base):
    __tablename__ = "user_skill_profile"
    __table_args__ = (UniqueConstraint("user_id", "track_id", name="uq_user_skill_profile_user_track"),)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    track_id = Column(Integer, ForeignKey("learning_tracks.id"))
    skill_score = Column(Float, default=0.1)
    confidence_score = Column(Float, default=0.1)
    attempts = Column(Integer)
