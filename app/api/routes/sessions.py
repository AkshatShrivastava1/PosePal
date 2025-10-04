import json
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from datetime import datetime
from app.db.session import get_session, init_db
from app.db.models import SessionDB, SessionMetric
from app.schemas.session import (
    SessionStartRequest, SessionStartResponse, MetricsIngest, SessionStopRequest, SessionSummary
)
from sqlmodel import Session as SQLSession

router = APIRouter()
init_db()

@router.post("/start", response_model=SessionStartResponse)
def start_session(payload: SessionStartRequest, db: SQLSession = Depends(get_session)):
    s = SessionDB(exercise=payload.exercise, user_id=payload.user_id, start_ts=datetime.utcnow())
    db.add(s)
    db.commit()
    db.refresh(s)
    return SessionStartResponse(session_id=s.id)

@router.post("/{session_id}/metrics")
def ingest_metrics(session_id: int, m: MetricsIngest, db: SQLSession = Depends(get_session)):
    s = db.get(SessionDB, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    rec = SessionMetric(
        session_id=session_id,
        reps=m.reps,
        avg_score=m.avg_score,
        flags_json=json.dumps(m.flags),
        duration_sec=m.duration_sec,
        ts=m.ts,
    )
    db.add(rec)
    db.commit()
    return {"ok": True}

@router.post("/{session_id}/stop")
def stop_session(session_id: int, payload: SessionStopRequest, db: SQLSession = Depends(get_session)):
    s = db.get(SessionDB, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    s.end_ts = payload.ts
    db.add(s)
    db.commit()
    return {"ok": True}

@router.get("/{session_id}/summary", response_model=SessionSummary)
def session_summary(session_id: int, db: SQLSession = Depends(get_session)):
    s = db.get(SessionDB, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    metrics = db.exec(select(SessionMetric).where(SessionMetric.session_id == session_id)).all()
    total_reps = sum(m.reps for m in metrics)
    avg_score = (sum(m.avg_score for m in metrics) / len(metrics)) if metrics else 0.0

    from collections import Counter
    c = Counter()
    for m in metrics:
        try:
            flags = json.loads(m.flags_json)
        except Exception:
            flags = []
        c.update(flags)
    top_flags = [f for f, _ in c.most_common(5)]
    duration = sum(m.duration_sec for m in metrics)

    return SessionSummary(
        session_id=session_id,
        total_reps=total_reps,
        avg_score=round(avg_score, 2),
        top_flags=top_flags,
        duration_sec=duration,
        exercise=s.exercise,
        start_ts=s.start_ts,
        end_ts=s.end_ts,
    )
