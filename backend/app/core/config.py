from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AI Trainer Backend"
    APP_ENV: str = "dev"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:5173,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:5175,http://127.0.0.1:5175"
    DATABASE_URL: str = "sqlite:///./trainer.db"
    GEMINI_API_KEY: str | None = "AIzaSyAkWoioVVFkxZFzqZBIGxX4SgINSCKMfS4"
    GEMINI_MODEL: str = "gemini-1.5-flash"

    class Config:
        env_file = ".env"

settings = Settings()
