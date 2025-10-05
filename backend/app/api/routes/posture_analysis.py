from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as SQLSession, select
from app.db.session import get_session
from app.db.models import SessionDB, AnnotatedFrame, SessionMetric
from app.services.gemini_service import get_gemini_analyzer
from app.schemas.posture_analysis import (
    SessionAnalysisRequest, 
    SessionAnalysisResponse, 
    SessionCleanupResponse,
    PostureAnalysis
)
from app.core.config import settings
from datetime import datetime
import json

router = APIRouter()

@router.post("/analyze", response_model=SessionAnalysisResponse)
def analyze_session_posture(
    request: SessionAnalysisRequest, 
    db: SQLSession = Depends(get_session)
):
    """
    Analyze a workout session's posture using Gemini AI and generate suggestions
    """
    print(f"🔍 [ANALYSIS ROUTE] Starting analysis for session {request.session_id}")
    
    try:
        # Verify session exists
        session = db.get(SessionDB, request.session_id)
        if not session:
            print(f"❌ [ANALYSIS ROUTE] Session {request.session_id} not found")
            raise HTTPException(status_code=404, detail="Session not found")
        
        print(f"🔍 [ANALYSIS ROUTE] Session found: exercise={session.exercise}, end_ts={session.end_ts}")
        
        # Check if session has ended
        if not session.end_ts:
            print(f"❌ [ANALYSIS ROUTE] Session {request.session_id} not ended")
            raise HTTPException(
                status_code=400, 
                detail="Session must be ended before analysis can be performed"
            )
        
        # Perform Gemini analysis
        try:
            print(f"🔍 [ANALYSIS ROUTE] Getting Gemini analyzer...")
            analyzer = get_gemini_analyzer()
            print(f"🔍 [ANALYSIS ROUTE] Calling analyze_session_posture...")
            analysis_result = analyzer.analyze_session_posture(
                request.session_id, 
                session.exercise, 
                db
            )
            print(f"🔍 [ANALYSIS ROUTE] Analysis result received: {analysis_result.get('status', 'unknown')}")
        except ValueError as e:
            raise HTTPException(
                status_code=503, 
                detail=f"AI analysis service unavailable: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Analysis failed: {str(e)}"
            )
        
        if analysis_result["status"] == "error":
            raise HTTPException(
                status_code=500, 
                detail=analysis_result["message"]
            )
        
        # Parse suggestions into structured format
        suggestions_data = analysis_result.get("suggestions", {})
        posture_analysis = None
        
        if suggestions_data and "overall_assessment" in suggestions_data:
            posture_analysis = PostureAnalysis(
                overall_assessment=suggestions_data.get("overall_assessment", ""),
                strengths=suggestions_data.get("strengths", []),
                areas_for_improvement=suggestions_data.get("areas_for_improvement", []),
                specific_suggestions=suggestions_data.get("specific_suggestions", []),
                exercise_specific_tips=suggestions_data.get("exercise_specific_tips", []),
                next_session_focus=suggestions_data.get("next_session_focus", "")
            )
        
        return SessionAnalysisResponse(
            status="success",
            session_id=request.session_id,
            exercise=session.exercise,
            total_keyframes=analysis_result["total_keyframes"],
            analyzed_keyframes=analysis_result["analyzed_keyframes"],
            suggestions=posture_analysis,
            analysis_timestamp=datetime.fromisoformat(analysis_result["analysis_timestamp"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/cleanup/{session_id}", response_model=SessionCleanupResponse)
def cleanup_session_data(session_id: int, db: SQLSession = Depends(get_session)):
    """
    Delete all session data including keyframes after analysis is complete
    """
    try:
        # Verify session exists
        session = db.get(SessionDB, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Count keyframes before deletion
        keyframes = db.exec(
            select(AnnotatedFrame).where(AnnotatedFrame.session_id == session_id)
        ).all()
        keyframe_count = len(keyframes)
        
        # Delete all keyframes for this session
        for keyframe in keyframes:
            db.delete(keyframe)
        
        # Delete all session metrics
        metrics = db.exec(
            select(SessionMetric).where(SessionMetric.session_id == session_id)
        ).all()
        for metric in metrics:
            db.delete(metric)
        
        # Delete the session itself
        db.delete(session)
        
        # Commit all deletions
        db.commit()
        
        return SessionCleanupResponse(
            status="success",
            session_id=session_id,
            deleted_keyframes=keyframe_count,
            deleted_session=True,
            message=f"Successfully deleted {keyframe_count} keyframes and session data"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.post("/analyze-and-cleanup/{session_id}")
def analyze_and_cleanup_session(session_id: int, db: SQLSession = Depends(get_session)):
    """
    Combined endpoint: analyze session posture and then clean up all data
    """
    try:
        # First, perform the analysis
        analysis_request = SessionAnalysisRequest(session_id=session_id)
        analysis_result = analyze_session_posture(analysis_request, db)
        
        # Then, clean up the data
        cleanup_result = cleanup_session_data(session_id, db)
        
        return {
            "analysis": analysis_result,
            "cleanup": cleanup_result,
            "message": "Session analyzed and cleaned up successfully"
        }
        
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Combined operation failed: {str(e)}")

@router.get("/debug/gemini-status")
def debug_gemini_status():
    """
    Debug endpoint to check Gemini service status
    """
    try:
        analyzer = get_gemini_analyzer()
        return {
            "status": "success",
            "message": "Gemini service initialized successfully",
            "api_key_configured": bool(settings.GEMINI_API_KEY),
            "api_key_length": len(settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "api_key_configured": bool(settings.GEMINI_API_KEY),
            "api_key_length": len(settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else 0
        }

@router.get("/{session_id}/keyframes/count")
def get_keyframe_count(session_id: int, db: SQLSession = Depends(get_session)):
    """
    Get the count of keyframes for a session (useful for checking before analysis)
    """
    try:
        keyframes = db.exec(
            select(AnnotatedFrame).where(AnnotatedFrame.session_id == session_id)
        ).all()
        
        return {
            "session_id": session_id,
            "keyframe_count": len(keyframes),
            "will_sample": len(keyframes) > 150,
            "sample_size": min(150, len(keyframes)) if len(keyframes) > 150 else len(keyframes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to count keyframes: {str(e)}")
