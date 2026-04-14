from pydantic import BaseModel
from typing import Optional

class UserSkillProfile(BaseModel):
    id: Optional[int] = None
    user_id: int
    track_id: int
    track_name: str          # ← NEW: for frontend titles/cards
    track_type: str          # ← NEW: 'python', 'javascript', etc. for Bootstrap accent/icons
    skill_score: float
    confidence_score: float
    attempts: int

    model_config = {
        "from_attributes": True
    }