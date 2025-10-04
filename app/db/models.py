from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    display_name: str | None = None

class SessionDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    exercise: str
    start_ts: datetime
    end_ts: datetime | None = None

class SessionMetric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="sessiondb.id")
    reps: int = 0
    avg_score: float = 0.0
    flags_json: str = "[]"
    duration_sec: int = 0
    ts: datetime
