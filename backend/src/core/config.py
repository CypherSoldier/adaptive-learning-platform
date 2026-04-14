from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    OPENAI_API_KEY: str = "your-key"
    DEBUG: bool = True

settings = Settings()