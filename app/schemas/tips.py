from pydantic import BaseModel
from typing import List

class TipsRequest(BaseModel):
    exercise: str
    flags: List[str] = []
    level: str = "beginner"

class TipsResponse(BaseModel):
    tips: List[str]
    source: str  # 'gemini' or 'rule-based'
