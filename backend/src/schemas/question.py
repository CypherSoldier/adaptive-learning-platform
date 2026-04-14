from pydantic import BaseModel

class QuestionOut(BaseModel):
    id: int
    question: str
    options : list[str]
    correct_answer: int
    explanation: str
    difficulty: int
    track_id: int
    source: str

    class Config:
        orm_mode = True