from pydantic import BaseModel

class SubmissionCreate(BaseModel):
    question_id: int
    answer: int
    track_id: int

class SubmissionOut(BaseModel):
    id: int
    user_id: int
    question_id: int
    answer: int
    is_correct: bool
    track_id: int

    model_config = {
        "from_attributes": True
    }

# NEW: Combined response for the submit endpoint
class SubmissionResponse(BaseModel):
    submission: SubmissionOut
    updated_skill_profile: dict   # or create a small model if you want stricter typing

    model_config = {
        "from_attributes": True
    }