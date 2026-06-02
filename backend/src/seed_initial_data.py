import json
import os
import sys
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.session import SessionLocal
from src.models.learning_track import LearningTrack
from src.models.question import Question


def seed_tracks():
    """Seed learning tracks from sample_lt.json"""
    db: Session = SessionLocal()
    try:
        json_path = "utils/sample_lt.json"
        with open(json_path, "r", encoding="utf-8") as f:
            tracks_data = json.load(f)

        seeded = 0
        for data in tracks_data:
            existing = db.query(LearningTrack).filter_by(id=data.get("id")).first()
            if not existing:
                track = LearningTrack(
                    id=data.get("id"),
                    track_type=data.get("track_type"),
                    name=data.get("name"),
                    description=data.get("description"),
                    difficulty_base=data.get("difficulty_base"),
                )
                db.add(track)
                seeded += 1

        db.commit()
        print(f"✅ Seeded {seeded} new learning tracks")
    finally:
        db.close()


def seed_questions():
    """Seed questions from all sample JSON files"""
    db: Session = SessionLocal()
    try:
        # Define your sample files
        sample_files = [
            "utils/sample_py.json",
            "utils/sample_cpp.json",
            "utils/sample_js.json",
        ]

        total_seeded = 0

        for file_path in sample_files:
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_path}")
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                questions_data = json.load(f)

            seeded_in_file = 0
            for q_data in questions_data:
                # Extract main track (e.g. "Python" from "Python – Time Complexity")
                topic_name = q_data.get("topic", "General")
                main_track_name = topic_name.split("–")[0].strip()

                # Find track
                track = db.query(LearningTrack).filter(
                    LearningTrack.name.ilike(f"%{main_track_name}%") |
                    LearningTrack.track_type.ilike(f"%{main_track_name}%")
                ).first()

                if not track:
                    print(f"⚠️  No track found for: {topic_name}")
                    continue

                # Check if question already exists
                existing = db.query(Question).filter(
                    Question.question == q_data.get("question")
                ).first()

                if not existing:
                    question = Question(
                        track_id=track.id,
                        question=q_data.get("question"),
                        options=q_data.get("options"),
                        correct_answer=q_data.get("correct_answer"),
                        explanation=q_data.get("explanation"),
                        difficulty=str(q_data.get("difficulty", 2)),
                        source=os.path.basename(file_path),
                    )
                    db.add(question)
                    seeded_in_file += 1
                    total_seeded += 1

            db.commit()
            print(f"✅ Loaded {seeded_in_file} new questions from {os.path.basename(file_path)}")

        print(f"🎉 Total new questions seeded: {total_seeded}")

    except Exception as e:
        print(f"❌ Error seeding questions: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# Run both when script is executed directly
if __name__ == "__main__":
    seed_tracks()
    seed_questions()