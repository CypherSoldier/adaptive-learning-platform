from datetime import datetime, timezone
from uuid import uuid4
import logging
import random
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from src.models.question import Question
from src.models.learning_track import LearningTrack
from src.services.skill_profile_service import get_or_create_skill_profile
from src.models.ai_generation_request import AIGenerationRequest
from src.models.submission import Submission
from src.models.user_question_progress import UserQuestionProgress, TrackOnboarding, LearningSession, LearningSessionQuestion
from src.ai_pipeline.ai_generate_mcq import generate_mcq

logger = logging.getLogger(__name__)
SEEDED_SOURCE_BY_TRACK = {1: "sample_py.json", 2: "sample_cpp.json", 3: "sample_js.json"}
SESSION_SIZE = 10
MAX_EXISTING = 5
GENERATION_ATTEMPTS = 3


def _session_questions(db: Session, session: LearningSession):
    return (db.query(Question)
        .join(LearningSessionQuestion, LearningSessionQuestion.question_id == Question.id)
        .filter(LearningSessionQuestion.session_id == session.id)
        .order_by(LearningSessionQuestion.position).all())


def _response(db: Session, session: LearningSession):
    return {"session_id": session.id, "session_type": session.session_type,
            "track_id": session.track_id, "questions": _session_questions(db, session)}


def _validated_question(item):
    if not isinstance(item, dict):
        return None
    question = item.get("question")
    options = item.get("options")
    explanation = item.get("explanation")
    try:
        correct_answer = int(item.get("correct_answer"))
        difficulty = int(float(item.get("difficulty")))
    except (TypeError, ValueError):
        return None
    if (not isinstance(question, str) or not question.strip()
            or not isinstance(explanation, str) or not explanation.strip()
            or not isinstance(options, list) or len(options) < 2
            or not all(isinstance(option, str) and option.strip() for option in options)
            or correct_answer < 0 or correct_answer >= len(options)
            or difficulty < 1 or difficulty > 5):
        return None
    return {"question": question, "options": options, "correct_answer": correct_answer,
            "explanation": explanation, "difficulty": difficulty}


def create_session(db: Session, user_id: int, track_id: int, idempotency_key: str):
    user_id = int(user_id)
    if not idempotency_key or len(idempotency_key) > 255:
        raise HTTPException(status_code=422, detail="Invalid Idempotency-Key")
    previous = db.query(LearningSession).filter_by(idempotency_key=idempotency_key).first()
    if previous:
        if previous.user_id != user_id or previous.track_id != track_id:
            raise HTTPException(status_code=409, detail="Idempotency key was already used for a different request")
        return _response(db, previous)
    if not db.query(LearningTrack).filter_by(id=track_id).first():
        raise HTTPException(status_code=404, detail="Track not found")

    legacy_request = db.query(AIGenerationRequest).filter_by(request_id=idempotency_key).first()
    if legacy_request:
        if legacy_request.user_id != user_id or legacy_request.track_id != track_id:
            raise HTTPException(status_code=409, detail="Idempotency key was already used for a different request")
        legacy_questions = db.query(Question).filter(
            Question.id.in_(legacy_request.question_ids), Question.track_id == track_id
        ).all() if legacy_request.question_ids else []
        question_by_id = {question.id: question for question in legacy_questions}
        ordered_questions = [question_by_id[qid] for qid in legacy_request.question_ids if qid in question_by_id]
        session = LearningSession(id=str(uuid4()), idempotency_key=idempotency_key,
                                  user_id=user_id, track_id=track_id, session_type="ai")
        db.add(session)
        try:
            db.flush()
            for position, question in enumerate(ordered_questions):
                if db.query(UserQuestionProgress).filter_by(user_id=user_id, question_id=question.id).first() is None:
                    db.add(UserQuestionProgress(user_id=user_id, question_id=question.id, completed=False, is_seeded=False))
                db.add(LearningSessionQuestion(session_id=session.id, question_id=question.id, position=position))
            db.commit()
        except IntegrityError:
            db.rollback()
            return _retry_or_conflict(db, user_id, track_id, idempotency_key)
        db.refresh(session)
        return _response(db, session)

    onboarding = db.query(TrackOnboarding).filter_by(user_id=user_id, track_id=track_id).first()
    if onboarding is None:
        # Existing users are backfilled complete by migration; a missing row
        # belongs to an account created after deployment.
        onboarding = TrackOnboarding(user_id=user_id, track_id=track_id, completed=False)
        db.add(onboarding)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            return _retry_or_conflict(db, user_id, track_id, idempotency_key)

    if not onboarding.completed:
        source = SEEDED_SOURCE_BY_TRACK.get(track_id)
        if source is None:
            raise HTTPException(status_code=500, detail="No seeded question set configured for track")
        seeded = db.query(Question).filter_by(track_id=track_id, source=source).order_by(Question.id).all()
        if len(seeded) != 15:
            raise HTTPException(status_code=503, detail=f"Expected 15 seeded questions for track {track_id}; found {len(seeded)}")
        for question in seeded:
            progress = db.query(UserQuestionProgress).filter_by(user_id=user_id, question_id=question.id).first()
            if progress is None:
                db.add(UserQuestionProgress(user_id=user_id, question_id=question.id, is_seeded=True))
            else:
                progress.is_seeded = True
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            return _retry_or_conflict(db, user_id, track_id, idempotency_key)
        submitted_question_ids = (db.query(Submission.question_id)
            .filter(Submission.user_id == user_id, Submission.track_id == track_id)
            .distinct())
        outstanding = (db.query(Question)
            .join(UserQuestionProgress, UserQuestionProgress.question_id == Question.id)
            .filter(UserQuestionProgress.user_id == user_id, UserQuestionProgress.is_seeded.is_(True), Question.track_id == track_id, ~Question.id.in_(submitted_question_ids))
            .order_by(Question.id).all())
        if not outstanding:
            onboarding.completed = True
            db.flush()
        else:
            get_or_create_skill_profile(db, user_id, track_id)
            session = LearningSession(id=str(uuid4()), idempotency_key=idempotency_key, user_id=user_id, track_id=track_id, session_type="onboarding")
            db.add(session)
            try:
                db.flush()
                for pos, question in enumerate(outstanding):
                    db.add(LearningSessionQuestion(session_id=session.id, question_id=question.id, position=pos))
                db.commit()
            except IntegrityError:
                db.rollback()
                return _retry_or_conflict(db, user_id, track_id, idempotency_key)
            db.refresh(session)
            return _response(db, session)

    profile = get_or_create_skill_profile(db, user_id, track_id)

    eligible_query = (db.query(Question)
        .outerjoin(UserQuestionProgress, (UserQuestionProgress.question_id == Question.id) & (UserQuestionProgress.user_id == user_id))
        .filter(Question.track_id == track_id, or_(Question.source != SEEDED_SOURCE_BY_TRACK.get(track_id, ""), Question.source.is_(None)))
        .filter((UserQuestionProgress.id.is_(None)) | (UserQuestionProgress.completed.is_(False))))
    eligible = eligible_query.order_by(Question.id).all()
    difficulty = max(1, min(5, round((profile.skill_score or 0.3) / 2)))
    difficulty_matched = []
    for question in eligible:
        try:
            question_difficulty = int(float(question.difficulty))
        except (TypeError, ValueError):
            continue
        if abs(question_difficulty - difficulty) <= 1:
            difficulty_matched.append(question)
    if difficulty_matched:
        eligible = difficulty_matched
    random.shuffle(eligible)
    existing = eligible[:MAX_EXISTING]
    ai_count = SESSION_SIZE - len(existing)
    track = db.query(LearningTrack).filter_by(id=track_id).first()
    topic = track.name or track.track_type or f"Track {track_id}"
    raw_questions = []
    try:
        for attempt in range(GENERATION_ATTEMPTS):
            needed = ai_count - len(raw_questions)
            if needed <= 0:
                break
            generated = generate_mcq(topic, difficulty, needed)
            for item in generated:
                validated = _validated_question(item)
                if validated:
                    raw_questions.append(validated)
                if len(raw_questions) == ai_count:
                    break
        if len(raw_questions) < ai_count:
            raise ValueError(f"Generator supplied {len(raw_questions)} of {ai_count} required AI questions")
    except Exception as exc:
        logger.exception("Question generation failed for user %s track %s", user_id, track_id)
        db.rollback()
        raise HTTPException(status_code=503, detail="Unable to generate a complete session; please retry with a new idempotency key") from exc

    session = LearningSession(id=str(uuid4()), idempotency_key=idempotency_key, user_id=user_id, track_id=track_id, session_type="ai")
    db.add(session)
    try:
        db.flush()
        questions = list(existing)
        generated_questions = []
        for item in raw_questions:
            question = Question(track_id=track_id, question=item["question"], options=item["options"], correct_answer=item["correct_answer"], explanation=item["explanation"], difficulty=item["difficulty"], source="ai_generated")
            db.add(question)
            generated_questions.append(question)
        db.flush()
        questions.extend(generated_questions)
        random.shuffle(questions)
        for position, question in enumerate(questions):
            progress = db.query(UserQuestionProgress).filter_by(user_id=user_id, question_id=question.id).first()
            if progress is None:
                db.add(UserQuestionProgress(user_id=user_id, question_id=question.id, completed=False, is_seeded=False))
            db.add(LearningSessionQuestion(session_id=session.id, question_id=question.id, position=position))
        db.commit()
    except IntegrityError:
        db.rollback()
        return _retry_or_conflict(db, user_id, track_id, idempotency_key)
    db.refresh(session)
    return _response(db, session)


def _retry_or_conflict(db, user_id, track_id, idempotency_key):
    winner = db.query(LearningSession).filter_by(idempotency_key=idempotency_key).first()
    if winner and winner.user_id == user_id and winner.track_id == track_id:
        return _response(db, winner)
    if winner:
        raise HTTPException(status_code=409, detail="Idempotency key was already used for a different request")
    raise HTTPException(status_code=409, detail="Session changed concurrently; retry with a new idempotency key")


