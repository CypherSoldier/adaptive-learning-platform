import datetime
from ..schemas.user_skill_profile import UserSkillProfile
from ..schemas.submission import SubmissionCreate, SubmissionOut

"""
def get_next_difficulty(last_result: str):
    if last_result == "passed":
        return "medium"
    return "easy"
"""


def update_skill_after_submission(
    skill_profile: UserSkillProfile, submission_out: SubmissionOut
) -> UserSkillProfile:
    if submission_out.is_correct:
        skill_profile.skill_score = min(1.0, skill_profile.skill_score + 0.08)
        skill_profile.confidence_score = min(1.0, skill_profile.confidence_score + 0.05)
    else:
        skill_profile.skill_score = max(0.0, skill_profile.skill_score - 0.06)
        skill_profile.confidence_score = max(0.0, skill_profile.confidence_score - 0.04)

    skill_profile.attempts += 1

    current_difficulty = skill_profile.skill_score

    if skill_profile.skill_score > 0.75:
        next_difficulty = min(5, current_difficulty + 1)
    elif skill_profile.skill_score < 0.35:
        next_difficulty = max(1, current_difficulty - 1)

    return skill_profile
