from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from datetime import datetime
import json
from app.db.session import get_session
from app.db.models import AnnotatedFrame, SessionDB
from app.schemas.keyframes import KeyframeRequest, KeyframeResponse, KeyframeListResponse
from app.services.keyframe_detector import keyframe_detector
from sqlmodel import Session as SQLSession

router = APIRouter()

@router.post("/keyframes", response_model=KeyframeResponse)
def store_keyframe(keyframe: KeyframeRequest, db: SQLSession = Depends(get_session)):
    """Store an annotated keyframe"""
    
    # Verify session exists
    session = db.get(SessionDB, keyframe.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Create annotated frame record
    annotated_frame = AnnotatedFrame(
        session_id=keyframe.session_id,
        frame_data=keyframe.frame_data,
        keyframe_type=keyframe.keyframe_type,
        timestamp=datetime.now(),
        exercise=keyframe.exercise,
        pose_landmarks=json.dumps(keyframe.pose_landmarks)
    )
    
    db.add(annotated_frame)
    db.commit()
    db.refresh(annotated_frame)
    
    return KeyframeResponse(
        id=annotated_frame.id,
        session_id=annotated_frame.session_id,
        keyframe_type=annotated_frame.keyframe_type,
        timestamp=annotated_frame.timestamp,
        exercise=annotated_frame.exercise
    )

@router.get("/sessions/{session_id}/keyframes", response_model=KeyframeListResponse)
def get_session_keyframes(session_id: int, db: SQLSession = Depends(get_session)):
    """Get all keyframes for a session"""
    
    # Verify session exists
    session = db.get(SessionDB, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get keyframes
    keyframes = db.exec(
        select(AnnotatedFrame).where(AnnotatedFrame.session_id == session_id)
        .order_by(AnnotatedFrame.timestamp)
    ).all()
    
    keyframe_responses = [
        KeyframeResponse(
            id=kf.id,
            session_id=kf.session_id,
            keyframe_type=kf.keyframe_type,
            timestamp=kf.timestamp,
            exercise=kf.exercise
        )
        for kf in keyframes
    ]
    
    return KeyframeListResponse(
        keyframes=keyframe_responses,
        total_count=len(keyframe_responses)
    )

@router.delete("/sessions/{session_id}/keyframes")
def clear_session_keyframes(session_id: int, db: SQLSession = Depends(get_session)):
    """Clear all keyframes for a session"""
    
    # Verify session exists
    session = db.get(SessionDB, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete keyframes
    keyframes = db.exec(
        select(AnnotatedFrame).where(AnnotatedFrame.session_id == session_id)
    ).all()
    
    for kf in keyframes:
        db.delete(kf)
    
    db.commit()
    
    # Reset detector state
    keyframe_detector.reset_session(session_id)
    
    return {"message": f"Cleared {len(keyframes)} keyframes for session {session_id}"}

@router.get("/sessions/{session_id}/rep-count")
def get_session_rep_count(session_id: int, db: SQLSession = Depends(get_session)):
    """Get current rep count for a session"""
    
    # Verify session exists
    session = db.get(SessionDB, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get rep count from detector
    rep_count = keyframe_detector.get_rep_count(session_id)
    
    return {
        "session_id": session_id,
        "exercise": session.exercise,
        "rep_count": rep_count,
        "counts_reps": session.exercise in ['squat', 'pushup', 'lunges']
    }
