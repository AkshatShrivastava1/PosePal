from pydantic import BaseModel
from typing import List

class FrameRequest(BaseModel):
    frame: str  # Base64 encoded image data
