from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class KeyframeRequest(BaseModel):
    session_id: int
    frame_data: str  # Base64 encoded annotated frame
    keyframe_type: str  # 'bottom', 'top', 'middle', 'plank_interval'
    exercise: str
    pose_landmarks: List[dict] = []

class KeyframeResponse(BaseModel):
    id: int
    session_id: int
    keyframe_type: str
    timestamp: datetime
    exercise: str

class KeyframeListResponse(BaseModel):
    keyframes: List[KeyframeResponse]
    total_count: int
