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

    model_config = {"from_attributes": True}


class SubmissionResponse(BaseModel):
    submission: SubmissionOut
    updated_skill_profile: dict 

    model_config = {"from_attributes": True}
