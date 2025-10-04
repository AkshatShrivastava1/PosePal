from fastapi import APIRouter
from app.schemas.tips import TipsRequest, TipsResponse
from app.services.tips import gemini_tips, rule_based_tips

router = APIRouter()

@router.post("/tips", response_model=TipsResponse)
def generate_tips(payload: TipsRequest):
    tips = gemini_tips(payload.exercise, payload.flags, payload.level)
    source = "gemini" if tips else "rule-based"
    if not tips:
        tips = rule_based_tips(payload.exercise, payload.flags, payload.level)
    return TipsResponse(tips=tips, source=source)
