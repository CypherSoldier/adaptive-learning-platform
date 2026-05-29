from pydantic import BaseModel
from typing import Optional


class LearningTrackBase(BaseModel):
    id: int
    track_type: str  # 'python', 'cpp', 'javascript'
    name: str
    description: str
    difficulty_base: str


class LearningTrackCreate(LearningTrackBase):
    pass


class LearningTrack(LearningTrackBase):
    id: int

    model_config = {"from_attributes": True}


class JavascriptTrack(LearningTrack):
    name: str
    description: str
    difficulty_base: str
