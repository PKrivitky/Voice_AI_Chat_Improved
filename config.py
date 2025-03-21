import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "your-default-bot-token")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-default-openai-key")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/dbname")
    ASSISTANT_ID: Optional[str] = None

settings = Settings()
