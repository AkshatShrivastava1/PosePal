from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class PostureSuggestion(BaseModel):
    category: str
    issue: str
    suggestion: str
    priority: str  # High/Medium/Low

class PostureAnalysis(BaseModel):
    overall_assessment: str
    strengths: List[str]
    areas_for_improvement: List[str]
    specific_suggestions: List[PostureSuggestion]
    exercise_specific_tips: List[str]
    next_session_focus: str

class SessionAnalysisRequest(BaseModel):
    session_id: int

class SessionAnalysisResponse(BaseModel):
    status: str
    session_id: int
    exercise: str
    total_keyframes: int
    analyzed_keyframes: int
    suggestions: Optional[PostureAnalysis] = None
    analysis_timestamp: datetime
    message: Optional[str] = None

class SessionCleanupResponse(BaseModel):
    status: str
    session_id: int
    deleted_keyframes: int
    deleted_session: bool
    message: str
