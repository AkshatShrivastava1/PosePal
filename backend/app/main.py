
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PosePal"
    CORS_ORIGINS: str = "*"  
    secret_key: str = "your_secret_key_here"
    access_token_expire_minutes: int = 30

settings = Settings()

from app.api.routes import health, sessions, tips, auth

app = FastAPI(title=settings.APP_NAME)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(health.router, tags=["health"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(tips.router, tags=["tips"])

@app.get("/")
def root():
    return {"ok": True, "name": settings.APP_NAME}
