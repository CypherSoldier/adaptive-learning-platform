from pydantic import BaseModel

class QuestionOut(BaseModel):
    id: int
    question: str
    options: list[str]
    correct_answer: int
    explanation: str
    difficulty: int | str
    track_id: int
    source: str
    model_config = {"from_attributes": True}

class LearningSessionOut(BaseModel):
    session_id: str
    session_type: str
    track_id: int
    questions: list[QuestionOut]
