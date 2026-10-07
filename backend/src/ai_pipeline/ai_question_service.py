import logging
from sqlalchemy.orm import Session
from ..models.question import Question
from src.ai_pipeline.ai_generate_mcq import generate_mcq
from src.models.ai_generation_request import AIGenerationRequest

logger = logging.getLogger(__name__)

BATCH_SIZE = 10

def generate_and_store_questions(
    db: Session,
    user_id: int,
    track_id: int,
    skill_score: float,
    confidence_score: float,
    request_id: str,
) -> list[Question]:
    previous_request = db.query(AIGenerationRequest).filter_by(request_id=request_id).first()
    if previous_request:
        if previous_request.user_id != user_id or previous_request.track_id != track_id:
            raise ValueError("Idempotency key was already used for a different request")
        questions = db.query(Question).filter(
            Question.id.in_(previous_request.question_ids)
        ).all()
        questions_by_id = {question.id: question for question in questions}
        return [
            questions_by_id[question_id]
            for question_id in previous_request.question_ids
            if question_id in questions_by_id
        ]
    
    if track_id == 1:
        topic = "Python"
    elif track_id == 2:
        topic = "C++"
    elif track_id == 3:
        topic = "JavaScript"
    else:
        raise ValueError(f"Unknown track ID: {track_id}")
    
    difficulty = max(1.0, min(5.0, round(skill_score / 2, 1)))

    logger.info(f"Generating questions for user {user_id} on topic '{topic}' with skill score {skill_score} and confidence score {confidence_score}. Difficulty level: {difficulty}")

    raw_questions = generate_mcq(topic, difficulty, BATCH_SIZE)[:BATCH_SIZE]

    ai_questions = []

    for q in raw_questions:
        record = Question( 
            track_id=track_id,
            question=q["question"],
            options=q["options"],
            correct_answer=q["correct_answer"],
            explanation=q["explanation"],
            difficulty=q["difficulty"],
            source="ai_generated",
            completed=q.get("completed", False),
        )
        db.add(record)
        ai_questions.append(record)
    
    db.flush()
    db.add(AIGenerationRequest(
        request_id=request_id,
        user_id=user_id,
        track_id=track_id,
        question_ids=[question.id for question in ai_questions],
    ))
    db.commit()
    for q in ai_questions:
        db.refresh(q)

    return ai_questions
