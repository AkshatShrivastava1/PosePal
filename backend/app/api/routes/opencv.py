from fastapi import APIRouter, Depends, HTTPException
from app.services.frame_processor import process_frame
from app.schemas.opencv import FrameRequest
from app.schemas.keyframes import KeyframeRequest
from app.db.session import get_session
from app.db.models import SessionDB
from sqlmodel import Session as SQLSession
import cv2
import base64
import numpy as np
from PIL import Image
import io
import json

router = APIRouter()

@router.post("/frames/{session_id}")
def process_frame_endpoint(request: FrameRequest, session_id: int, db: SQLSession = Depends(get_session)):
    try:
        # Verify session exists and get exercise type
        session = db.get(SessionDB, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        exercise = session.exercise
        
        # Decode the base64 data URL
        # Remove the data URL prefix (e.g., "data:image/jpeg;base64,")
        if request.frame.startswith('data:image'):
            header, encoded = request.frame.split(',', 1)
            frame_data = base64.b64decode(encoded)
        else:
            # If it's just base64 without data URL prefix
            frame_data = base64.b64decode(request.frame)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(frame_data))
        
        # Convert PIL Image to OpenCV format (BGR)
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Process the frame with session info
        print(f"🔍 [OPENCV ROUTE] Session {session_id}: Calling process_frame with exercise={exercise}")
        result = process_frame(opencv_image, session_id=session_id, exercise=exercise)
        print(f"🔍 [OPENCV ROUTE] Session {session_id}: process_frame returned result keys: {list(result.keys())}")
        
        # If this is a keyframe, store it
        if result.get('should_save_keyframe') and result.get('keyframe_type'):
            print(f"💾 [KEYFRAME SAVE] Session {session_id}: Saving {result.get('keyframe_type')} keyframe to database")
            
            # Test database connection
            try:
                from sqlmodel import select
                test_query = db.exec(select(SessionDB).where(SessionDB.id == session_id)).first()
                print(f"🔍 [KEYFRAME DEBUG] Session {session_id}: Database connection test - found session: {test_query is not None}")
            except Exception as e:
                print(f"❌ [KEYFRAME DEBUG] Session {session_id}: Database connection test failed: {e}")
            
            # Create annotated frame record
            from app.db.models import AnnotatedFrame
            from datetime import datetime
            
            annotated_frame = AnnotatedFrame(
                session_id=session_id,
                frame_data=result['annotated_image'],
                keyframe_type=result['keyframe_type'],
                timestamp=datetime.now(),
                exercise=exercise,
                pose_landmarks=json.dumps([
                    {"name": name, "x": coords[0], "y": coords[1]} 
                    for name, coords in result.get('landmarks', {}).items()
                ] if result.get('landmarks') else [])
            )
            
            try:
                print(f"🔍 [KEYFRAME DEBUG] Session {session_id}: About to save keyframe")
                print(f"🔍 [KEYFRAME DEBUG] Session {session_id}: frame_data length: {len(annotated_frame.frame_data)}")
                print(f"🔍 [KEYFRAME DEBUG] Session {session_id}: keyframe_type: {annotated_frame.keyframe_type}")
                print(f"🔍 [KEYFRAME DEBUG] Session {session_id}: exercise: {annotated_frame.exercise}")
                print(f"🔍 [KEYFRAME DEBUG] Session {session_id}: pose_landmarks length: {len(annotated_frame.pose_landmarks)}")
                
                db.add(annotated_frame)
                print(f"🔍 [KEYFRAME DEBUG] Session {session_id}: Added to session")
                
                db.commit()
                print(f"🔍 [KEYFRAME DEBUG] Session {session_id}: Committed to database")
                
                db.refresh(annotated_frame)
                print(f"🔍 [KEYFRAME DEBUG] Session {session_id}: Refreshed object")
                
                result['keyframe_stored'] = True
                result['keyframe_id'] = annotated_frame.id
                print(f"✅ [KEYFRAME SAVED] Session {session_id}: Keyframe saved with ID {annotated_frame.id}")
            except Exception as e:
                print(f"❌ [KEYFRAME SAVE ERROR] Session {session_id}: Failed to save keyframe - {str(e)}")
                print(f"❌ [KEYFRAME SAVE ERROR] Session {session_id}: Exception type: {type(e)}")
                import traceback
                print(f"❌ [KEYFRAME SAVE ERROR] Session {session_id}: Traceback: {traceback.format_exc()}")
                db.rollback()
                result['keyframe_stored'] = False
                result['keyframe_id'] = None
        else:
            print(f"⏭️ [NO KEYFRAME] Session {session_id}: No keyframe to save (should_save={result.get('should_save_keyframe')}, type={result.get('keyframe_type')})")
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}