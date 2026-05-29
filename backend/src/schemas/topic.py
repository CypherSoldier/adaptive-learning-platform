from pydantic import BaseModel


class Topic(BaseModel):
    id: int
    track_id: int
    name: str
    difficulty_base: str
