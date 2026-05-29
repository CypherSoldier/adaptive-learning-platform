from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    DEBUG: bool = True


settings = Settings()
