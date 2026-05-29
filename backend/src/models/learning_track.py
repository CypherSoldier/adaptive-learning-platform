from sqlalchemy import Column, Integer, String
from src.database.session import Base


class LearningTrack(Base):
    __tablename__ = "learning_tracks"
    id = Column(Integer, primary_key=True, index=True)
    track_type = Column(String)  # 'python', 'cpp', 'javascript'
    name = Column(String)
    description = Column(String)
    difficulty_base = Column(String)
