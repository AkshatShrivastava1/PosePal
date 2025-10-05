from google import genai
import json
import base64
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os
from app.db.models import AnnotatedFrame
from sqlmodel import Session as SQLSession, select
from app.core.config import settings

class GeminiPostureAnalyzer:
    def __init__(self):
        # Configure Gemini API
        api_key = settings.GEMINI_API_KEY
        print(f"🔍 [GEMINI INIT] API key configured: {api_key is not None}")
        print(f"🔍 [GEMINI INIT] API key length: {len(api_key) if api_key else 0}")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        try:
            print(f"🔍 [GEMINI INIT] Initializing Gemini client...")
            self.client = genai.Client(api_key=api_key)
            print(f"🔍 [GEMINI INIT] Gemini client initialized successfully")
        except Exception as e:
            print(f"❌ [GEMINI INIT] Failed to initialize Gemini client: {e}")
            raise ValueError(f"Failed to initialize Gemini client: {str(e)}")
    
    def analyze_session_posture(
        self, 
        session_id: int, 
        exercise: str, 
        db: SQLSession
    ) -> Dict[str, any]:
        """
        Analyze a workout session's posture and generate suggestions
        """
        print(f"🔍 [GEMINI DEBUG] Starting analysis for session {session_id}, exercise: {exercise}")
        
        try:
            # Get all keyframes for the session
            keyframes = db.exec(
                select(AnnotatedFrame).where(AnnotatedFrame.session_id == session_id)
            ).all()
            
            print(f"🔍 [GEMINI DEBUG] Found {len(keyframes)} keyframes for session {session_id}")
            
            if not keyframes:
                print(f"⚠️ [GEMINI DEBUG] No keyframes found for session {session_id}")
                return {
                    "status": "success",
                    "session_id": session_id,
                    "exercise": exercise,
                    "total_keyframes": 0,
                    "analyzed_keyframes": 0,
                    "suggestions": {
                        "overall_assessment": "No pose data was captured during this session. Please ensure you are visible in the camera frame during your workout.",
                        "strengths": ["Session completed successfully"],
                        "areas_for_improvement": ["Ensure camera visibility", "Check pose detection"],
                        "specific_suggestions": [
                            {
                                "category": "Technical",
                                "issue": "No pose data captured",
                                "suggestion": "Make sure you are fully visible in the camera frame and well-lit during your workout",
                                "priority": "High"
                            }
                        ],
                        "exercise_specific_tips": [f"Position yourself clearly in view for {exercise} tracking"],
                        "next_session_focus": "Ensure proper camera positioning and lighting"
                    },
                    "analysis_timestamp": datetime.now().isoformat()
                }
            
            # Log keyframe details
            for i, kf in enumerate(keyframes):
                print(f"🔍 [GEMINI DEBUG] Keyframe {i+1}: type={kf.keyframe_type}, exercise={kf.exercise}, timestamp={kf.timestamp}")
            
            # Sample keyframes if too many (>150)
            sampled_keyframes = self._sample_keyframes(keyframes)
            print(f"🔍 [GEMINI DEBUG] Sampled to {len(sampled_keyframes)} keyframes")
            
            # Prepare data for Gemini analysis
            analysis_data = self._prepare_analysis_data(sampled_keyframes, exercise)
            print(f"🔍 [GEMINI DEBUG] Prepared analysis data with {len(analysis_data)} entries")
            
            # Generate posture analysis using Gemini
            print(f"🔍 [GEMINI DEBUG] Calling Gemini API...")
            suggestions = self._generate_posture_suggestions(analysis_data, exercise)
            print(f"🔍 [GEMINI DEBUG] Gemini analysis completed")
            
            return {
                "status": "success",
                "session_id": session_id,
                "exercise": exercise,
                "total_keyframes": len(keyframes),
                "analyzed_keyframes": len(sampled_keyframes),
                "suggestions": suggestions,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ [GEMINI DEBUG] Error in analyze_session_posture: {e}")
            print(f"❌ [GEMINI DEBUG] Exception type: {type(e)}")
            import traceback
            print(f"❌ [GEMINI DEBUG] Traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "message": f"Analysis failed: {str(e)}"
            }
    
    def _sample_keyframes(self, keyframes: List[AnnotatedFrame]) -> List[AnnotatedFrame]:
        """
        Sample keyframes evenly if there are more than 150
        """
        if len(keyframes) <= 150:
            return keyframes
        
        # Sort by timestamp to ensure chronological order
        sorted_keyframes = sorted(keyframes, key=lambda k: k.timestamp)
        
        # Calculate sampling interval
        total_count = len(sorted_keyframes)
        sample_count = 150
        interval = total_count / sample_count
        
        sampled = []
        for i in range(sample_count):
            index = int(i * interval)
            if index < total_count:
                sampled.append(sorted_keyframes[index])
        
        return sampled
    
    def _prepare_analysis_data(
        self, 
        keyframes: List[AnnotatedFrame], 
        exercise: str
    ) -> Dict[str, any]:
        """
        Prepare keyframe data for Gemini analysis
        """
        print(f"🔍 [GEMINI DEBUG] Preparing analysis data for {len(keyframes)} keyframes")
        
        analysis_data = {
            "exercise": exercise,
            "total_keyframes": len(keyframes),
            "keyframes": []
        }
        
        for i, keyframe in enumerate(keyframes):
            # Parse landmarks
            try:
                landmarks = json.loads(keyframe.pose_landmarks) if keyframe.pose_landmarks else []
                print(f"🔍 [GEMINI DEBUG] Keyframe {i+1}: parsed {len(landmarks)} landmarks")
            except Exception as e:
                landmarks = []
                print(f"⚠️ [GEMINI DEBUG] Keyframe {i+1}: error parsing landmarks: {e}")
            
            keyframe_data = {
                "keyframe_type": keyframe.keyframe_type,
                "timestamp": keyframe.timestamp.isoformat(),
                "landmarks": landmarks,
                "frame_data": keyframe.frame_data  # Include full image data
            }
            
            analysis_data["keyframes"].append(keyframe_data)
        
        return analysis_data
    
    def _generate_posture_suggestions(
        self, 
        analysis_data: Dict[str, any], 
        exercise: str
    ) -> Dict[str, any]:
        """
        Use Gemini to analyze posture and generate suggestions
        """
        prompt = self._create_analysis_prompt(analysis_data, exercise)
        print(f"🔍 [GEMINI DEBUG] Prompt length: {len(prompt)} characters")
        
        try:
            print(f"🔍 [GEMINI DEBUG] Calling Gemini API with model gemini-1.5-pro")
            print(f"🔍 [GEMINI DEBUG] About to call self.client.models.generate_content")
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            print(f"🔍 [GEMINI DEBUG] Gemini API response received")
            print(f"🔍 [GEMINI DEBUG] Response type: {type(response)}")
            
            suggestions_text = response.text
            print(f"🔍 [GEMINI DEBUG] Received response length: {len(suggestions_text)} characters")
            print(f"🔍 [GEMINI DEBUG] Response text preview: {suggestions_text[:200]}...")
            
            # Parse the response into structured suggestions
            suggestions = self._parse_suggestions(suggestions_text, exercise)
            print(f"🔍 [GEMINI DEBUG] Parsed suggestions successfully")
            
            return suggestions
            
        except Exception as e:
            print(f"❌ [GEMINI DEBUG] Error calling Gemini API: {e}")
            print(f"❌ [GEMINI DEBUG] Exception type: {type(e)}")
            import traceback
            print(f"❌ [GEMINI DEBUG] Traceback: {traceback.format_exc()}")
            # Return fallback suggestions
            return {
                "overall_assessment": f"Unable to analyze {exercise} form at this time. Please consult with a fitness professional for personalized feedback.",
                "strengths": ["Completed workout session"],
                "areas_for_improvement": ["AI analysis temporarily unavailable"],
                "specific_suggestions": [
                    {
                        "category": "Technical",
                        "issue": "Analysis service error",
                        "suggestion": "Please try again later or consult with a fitness professional",
                        "priority": "Medium"
                    }
                ],
                "exercise_specific_tips": [f"Focus on maintaining proper {exercise} form"],
                "next_session_focus": "Continue practicing with attention to form"
            }
    
    def _create_analysis_prompt(self, analysis_data: Dict[str, any], exercise: str) -> str:
        """
        Create a detailed prompt for Gemini analysis
        """
        prompt = f"""
You are a professional fitness trainer and posture expert. Analyze the following workout session data for a {exercise} exercise and provide detailed posture improvement suggestions.

EXERCISE: {exercise}
TOTAL KEYFRAMES ANALYZED: {analysis_data['total_keyframes']}

KEYFRAME DATA:
"""
        
        # Add keyframe information with images
        for i, keyframe in enumerate(analysis_data['keyframes'][:5]):  # Limit to first 5 for prompt length and cost
            prompt += f"""
Keyframe {i+1} ({keyframe['keyframe_type']} position):
- Timestamp: {keyframe['timestamp']}
- Landmarks: {len(keyframe['landmarks'])} detected points
"""
            
            # Add key landmark positions for analysis
            if keyframe['landmarks']:
                key_landmarks = ['LEFT_HIP', 'RIGHT_HIP', 'LEFT_KNEE', 'RIGHT_KNEE', 'LEFT_SHOULDER', 'RIGHT_SHOULDER']
                for landmark in keyframe['landmarks']:
                    if landmark.get('name') in key_landmarks:
                        prompt += f"  - {landmark['name']}: ({landmark.get('x', 'N/A')}, {landmark.get('y', 'N/A')})\n"
            
            # Add the image
            if keyframe.get('frame_data'):
                prompt += f"\nImage of {keyframe['keyframe_type']} position:\n{keyframe['frame_data']}\n"
        
        prompt += f"""

Please analyze the workout session by examining both the landmark coordinates and the visual images provided. Focus on:

1. **Visual Form Analysis**: Examine the images to assess body alignment, posture, and technique
2. **Landmark Validation**: Cross-reference the numerical coordinates with what you see in the images
3. **Range of Motion**: Evaluate the depth and quality of each exercise phase
4. **Body Alignment**: Check for proper spine, shoulder, and hip positioning
5. **Common Form Issues**: Look for typical mistakes like arching back, improper hand placement, etc.

Please provide your analysis in the following JSON format:

{{
    "overall_assessment": "Brief overall assessment of the workout session based on visual and numerical data",
    "strengths": ["List of 2-3 key strengths observed from the images and data"],
    "areas_for_improvement": ["List of 2-3 main areas needing improvement based on visual analysis"],
    "specific_suggestions": [
        {{
            "category": "Posture/Form",
            "issue": "Specific issue identified from the images",
            "suggestion": "Detailed improvement suggestion with visual cues",
            "priority": "High/Medium/Low"
        }}
    ],
    "exercise_specific_tips": ["Exercise-specific tips for {exercise} based on visual analysis"],
    "next_session_focus": "What to focus on in the next workout session based on current form"
}}
"""
        
        return prompt
    
    def _parse_suggestions(self, suggestions_text: str, exercise: str) -> Dict[str, any]:
        """
        Parse Gemini response into structured suggestions
        """
        try:
            # Try to extract JSON from the response
            import re
            
            # Look for JSON block in the response
            json_match = re.search(r'\{.*\}', suggestions_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                suggestions = json.loads(json_str)
                return suggestions
            else:
                # If no JSON found, create a structured response from text
                return {
                    "overall_assessment": "Analysis completed",
                    "strengths": ["Session completed successfully"],
                    "areas_for_improvement": ["Continue practicing form"],
                    "specific_suggestions": [
                        {
                            "category": "General",
                            "issue": "Form refinement needed",
                            "suggestion": suggestions_text[:200] + "...",
                            "priority": "Medium"
                        }
                    ],
                    "exercise_specific_tips": [f"Focus on proper {exercise} technique"],
                    "next_session_focus": "Continue building consistency"
                }
                
        except Exception as e:
            return {
                "overall_assessment": "Analysis completed with limitations",
                "strengths": ["Session data processed"],
                "areas_for_improvement": ["Form analysis needed"],
                "specific_suggestions": [
                    {
                        "category": "General",
                        "issue": "Analysis parsing error",
                        "suggestion": "Please review your form with a trainer",
                        "priority": "Medium"
                    }
                ],
                "exercise_specific_tips": [f"Focus on proper {exercise} technique"],
                "next_session_focus": "Continue practicing",
                "raw_response": suggestions_text
            }

# Global instance - will be initialized when first used
gemini_analyzer = None

def get_gemini_analyzer():
    """Get or create the Gemini analyzer instance"""
    global gemini_analyzer
    print(f"🔍 [GEMINI GET] Getting analyzer instance, current: {gemini_analyzer is not None}")
    if gemini_analyzer is None:
        print(f"🔍 [GEMINI GET] Creating new analyzer instance...")
        gemini_analyzer = GeminiPostureAnalyzer()
        print(f"🔍 [GEMINI GET] Analyzer instance created successfully")
    return gemini_analyzer
