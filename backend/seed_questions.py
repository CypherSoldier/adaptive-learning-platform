import json
import sys
import os

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.database.session import SessionLocal, engine, Base
from src.models.learning_track import LearningTrack

# from src.models.topic import Topic
from src.models.question import Question


def seed_questions():
    """Load questions from sample_mcq.json into the database"""

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Load the JSON file
        json_path = "src/utils/sample_js.json"
        with open(json_path, "r") as f:
            questions_data = json.load(f)

        # Create learning tracks if they don't exist
        # Learning tracks is in the database, so this may need to be modified/removed
        tracks_map = {}
        for track_name in ["Python", "C++", "JavaScript"]:
            track = (
                db.query(LearningTrack)
                .filter(LearningTrack.track_type == track_name)
                .first()
            )
            if not track:
                track = LearningTrack(
                    track_type=track_name.lower(),
                    name=track_name,
                    description=f"Learn {track_name}",
                    difficulty_base="intermediate",
                )
                db.add(track)
                db.commit()
                db.refresh(track)
            tracks_map[track_name] = track

        # Process each question
        for q_data in questions_data:
            topic_name = q_data.get("topic", "General")

            # Extract main track from topic (e.g., "Python" from "Python – Time Complexity")
            main_track = topic_name.split("–")[0].strip()

            # Find the track
            track = tracks_map.get(main_track)
            if not track:
                # Try to find it with slightly different matching
                for track_name, track_obj in tracks_map.items():
                    if track_name.lower() in main_track.lower():
                        track = track_obj
                        break

            if not track:
                print(f"Warning: Could not find track for topic '{topic_name}'")
                continue

            # Find or create topic
            """
            topic = db.query(Topic).filter(
                Topic.name == topic_name,
                Topic.track_id == track.id
            ).first()
            
            
            if not topic:
                topic = Topic(
                    track_id=track.id,
                    name=topic_name,
                    difficulty_base=str(q_data.get("difficulty", 2))
                )
                db.add(topic)
                db.commit()
                db.refresh(topic)
            """

            # Check if question already exists
            existing_q = (
                db.query(Question)
                .filter(Question.question == q_data.get("question"))
                .first()
            )

            if not existing_q:
                # Create question
                question = Question(
                    options=q_data.get("options"),
                    explanation=q_data.get("explanation"),
                    track_id=track.id,
                    difficulty=str(q_data.get("difficulty", 2)),
                    source="sample_mcq.json",
                    question=q_data.get("question"),
                    correct_answer=q_data.get("correct_answer"),
                )
                db.add(question)

        db.commit()
        print(
            f"Successfully loaded {len(questions_data)} questions from sample_mcq.json"
        )

    except Exception as e:
        print(f"Error seeding questions: {e}")
        db.rollback()
        raise
    finally:
        db.close()

    # pass


if __name__ == "__main__":
    seed_questions()
