from typing import List
from app.core.config import settings

try:
    from google import genai
except Exception:
    genai = None

DEFAULT_TIPS = {
    "squat": {
        "beginner": [
            "Keep heels down and push hips back first.",
            "Knees track over toes; avoid knees collapsing inward.",
            "Keep chest up; avoid rounding your back."
        ]
    },
    "pushup": {
        "beginner": [
            "Keep a straight line from shoulders to ankles.",
            "Hands under shoulders; elbows ~45°.",
            "Lower until chest is a fist from the floor."
        ]
    }
}

def rule_based_tips(exercise: str, flags: List[str], level: str) -> List[str]:
    ex = exercise.lower()
    bank = DEFAULT_TIPS.get(ex, {})
    tips = bank.get(level, []) or bank.get("beginner", [])
    flag_map = {
        "knees_in": "Drive knees out in line with your toes during the descent.",
        "shallow_depth": "Descend until hips reach knee level for a full rep.",
        "back_round": "Brace your core and keep chest up to avoid rounding.",
        "hip_sag": "Squeeze glutes and keep core tight to prevent hip sag.",
        "short_range": "Aim for full range each rep for consistency."
    }
    for f in flags:
        if f in flag_map and flag_map[f] not in tips:
            tips.append(flag_map[f])
    return tips[:5]

def gemini_tips(exercise: str, flags: List[str], level: str) -> List[str]:
    if not settings.GEMINI_API_KEY or genai is None:
        return []
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = (
            f"Give concise (<=5 bullets) coaching cues for a {exercise} at {level} level. "
            f"Flags: {', '.join(flags) if flags else 'none'}. "
            "Be actionable, short, and safe; no medical advice."
        )
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt)
        text = (getattr(resp, "text", None) or "").strip()
        lines = [l.strip("-• ").strip() for l in text.splitlines() if l.strip()][:5]
        return lines or ([text] if text else [])
    except Exception:
        return []
