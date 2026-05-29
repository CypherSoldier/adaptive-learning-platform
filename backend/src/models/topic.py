from sqlalchemy import Column, Integer, String, ForeignKey
from src.database.session import Base


class Topic(Base):
    __tablename__ = "topic"
    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"))
    name = Column(String)
    difficulty_base = Column(String)
