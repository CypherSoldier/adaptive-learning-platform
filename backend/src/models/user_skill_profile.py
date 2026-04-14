from sqlalchemy import Column, Integer, ForeignKey, Float
from src.database.session import Base

class UserSkillProfile(Base):
    __tablename__ = "user_skill_profile"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    track_id = Column(Integer, ForeignKey('learning_tracks.id'))
    skill_score = Column(Float, default=0.1)
    confidence_score = Column(Float, default=0.1)
    attempts = Column(Integer)