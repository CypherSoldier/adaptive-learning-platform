from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Time
from src.database.session import Base

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer = Column(Integer)
    is_correct = Column(Boolean)
    track_id = Column(Integer)
    time_taken = Column(Time)
    evaluated_by = Column(String)