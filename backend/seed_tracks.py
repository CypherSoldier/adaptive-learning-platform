import json
import sys
import os

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.database.session import SessionLocal, engine, Base
from src.models.learning_track import LearningTrack

def seed_tracks():
    """Load learning tracks from sample_lt.json into the database"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Load the JSON file
        json_path = "src/utils/sample_lt.json"
        with open(json_path, 'r') as f:
            tracks_data = json.load(f)
        
        # Process each track
        for q_data in tracks_data:
            # Check if track already exists
            existing_q = db.query(LearningTrack).filter(
                LearningTrack.id == q_data.get("id")
            ).first()
            
            if not existing_q:
                # Create question
                track = LearningTrack(
                    track_type=q_data.get("track_type"),
                    name=q_data.get("name"),
                    description=q_data.get("description"),
                    difficulty_base=q_data.get("difficulty_base")
                )
                db.add(track)
        
        db.commit()
        print(f"Successfully loaded {len(tracks_data)} tracks from sample_lt.json")
        
    except Exception as e:
        print(f"Error seeding tracks: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_tracks()

''' to delete all, replace everything in try: with
db.query(LearningTrack).delete()
db.commit()
print("Deleted")
'''