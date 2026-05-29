from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from src.database.session import Base


class AIQuestion(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    question = Column(String)
    options = Column(JSON)
    correct_answer = Column(Integer)
    explanation = Column(String)
    difficulty = Column(Integer)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"))
    source = Column(String)