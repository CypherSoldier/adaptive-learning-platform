# ERROR 1:
GET request test does not return questions. Only '[]' in the response body.

I load the questions as follows:
``` python
import json
import sys
import os

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.database.session import SessionLocal, engine, Base
from src.models.learning_track import LearningTrack
from src.models.topic import Topic
from src.models.question import Question

def seed_questions():
    """Load questions from sample_mcq.json into the database"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Load the JSON file
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "utils", "sample_mcq.json")
        with open(json_path, 'r') as f:
            questions_data = json.load(f)
        
        # Create learning tracks if they don't exist
        tracks_map = {}
        for track_name in ["Python", "C++", "JavaScript"]:
            track = db.query(LearningTrack).filter(
                LearningTrack.name == track_name
            ).first()
            if not track:
                track = LearningTrack(
                    track_type=track_name.lower(),
                    name=track_name,
                    description=f"Learn {track_name}",
                    difficulty_base="intermediate"
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
            
            # Check if question already exists
            existing_q = db.query(Question).filter(
                Question.question_text == q_data.get("question")
            ).first()
            
            if not existing_q:
                # Create question
                question = Question(
                    topic_id=topic.id,
                    type="mcq",
                    difficulty=str(q_data.get("difficulty", 2)),
                    source="sample_mcq.json",
                    question_text=q_data.get("question"),
                    correct_answer=q_data.get("correct_answer")
                )
                db.add(question)
        
        db.commit()
        print(f"Successfully loaded {len(questions_data)} questions from sample_mcq.json")
        
    except Exception as e:
        print(f"Error seeding questions: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_questions()
```

Server responds with 'Successfully loaded 15 questions from sample_mcq.json'

# ERROR 2
Performing a POST request test returns error code 500 'Internal Server Error'

Logs show:
```
ERROR:root:Failed to register user: david@example.com. Error: 'id' is an invalid keyword argument for User
INFO:     127.0.0.1:56730 - "POST /auth/ HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 407, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 69, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\fastapi\applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\applications.py", line 123, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\middleware\errors.py", line 186, in __call__
    raise exc
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\middleware\exceptions.py", line 65, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\_exception_handler.py", line 64, in wrapped_app
    raise exc
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\routing.py", line 756, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\routing.py", line 776, in app
    await route.handle(scope, receive, send)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\routing.py", line 297, in handle
    await self.app(scope, receive, send)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\routing.py", line 77, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\_exception_handler.py", line 64, in wrapped_app
    raise exc
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\starlette\routing.py", line 72, in app
    response = await func(request)
               ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\fastapi\routing.py", line 278, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\fastapi\routing.py", line 191, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\CalebWagner\Documents\portfolio_update\adaptive_learning\backend\src\api\routes\auth_routes.py", line 19, in register_user
    auth_service.register_user(db, register_user_request)
  File "C:\Users\CalebWagner\Documents\portfolio_update\adaptive_learning\backend\src\services\auth_service.py", line 62, in register_user
    create_user_model = User(
                        ^^^^^
  File "<string>", line 4, in __init__
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\sqlalchemy\orm\state.py", line 564, in _initialize_instance
    with util.safe_reraise():
         ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\sqlalchemy\util\langhelpers.py", line 146, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\sqlalchemy\orm\state.py", line 562, in _initialize_instance
    manager.original_init(*mixed[1:], **kwargs)
  File "C:\Users\CalebWagner\OdooC\server\Lib\site-packages\sqlalchemy\orm\decl_base.py", line 2139, in _declarative_constructor
    raise TypeError(
TypeError: 'id' is an invalid keyword argument for User
```

# Context which may help

auth_service.py
``` python
def register_user(db: Session, register_user_request: auth.RegisterUserRequest) -> None:
    try:
        create_user_model = User(
            id=register_user_request.id,
            email=register_user_request.email,
            full_name=register_user_request.full_name,
            password_hash=get_password_hash(register_user_request.password)
        )    
        db.add(create_user_model)
        db.commit()
    except Exception as e:
        logging.error(f"Failed to register user: {register_user_request.email}. Error: {str(e)}")
        raise
```

schemas/auth.py:
``` python
class RegisterUserRequest(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    password: str
```

routes/auth_routes.py
``` python
@router.post("/", status_code=status.HTTP_201_CREATED)
#@limiter.limit("5/hour")
async def register_user(request: Request, db: DbSession, register_user_request: auth.RegisterUserRequest):
    auth_service.register_user(db, register_user_request)
```

models/user.py:
``` python
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String)
```

