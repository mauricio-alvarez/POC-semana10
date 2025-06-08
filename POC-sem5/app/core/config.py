import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_API_KEY: str = os.getenv("DATABASE_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()