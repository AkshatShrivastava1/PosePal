from fastapi import APIRouter
from app.core.frame_processor import process_frame
from app.schemas.opencv import FrameRequest
import cv2
import base64
import numpy as np
from PIL import Image
import io

router = APIRouter()

@router.post("/frames")
def process_frame_endpoint(request: FrameRequest):
    try:
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
        
        # Process the frame
        result = process_frame(opencv_image)
        
        print(result)
        return {"status": "success", "result": result}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}