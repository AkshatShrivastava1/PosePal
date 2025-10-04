from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SessionStartRequest(BaseModel):
    exercise: str
    user_id: Optional[int] = None

class SessionStartResponse(BaseModel):
    session_id: int

class MetricsIngest(BaseModel):
    reps: int
    avg_score: float
    flags: List[str] = []
    duration_sec: int
    ts: datetime

class SessionStopRequest(BaseModel):
    ts: datetime

class SessionSummary(BaseModel):
    session_id: int
    total_reps: int
    avg_score: float
    top_flags: list[str]
    duration_sec: int
    exercise: str
    start_ts: datetime
    end_ts: datetime | None = None
