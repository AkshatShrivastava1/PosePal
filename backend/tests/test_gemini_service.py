import pytest
from unittest.mock import patch, MagicMock
from app.services.gemini_service import GeminiPostureAnalyzer
from app.db.models import AnnotatedFrame
from datetime import datetime
import json

class TestGeminiPostureAnalyzer:
    def setup_method(self):
        # Mock the Gemini API key
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel'):
                    self.analyzer = GeminiPostureAnalyzer()
    
    def test_sample_keyframes_small_session(self):
        """Test that small sessions (<150 keyframes) are not sampled"""
        keyframes = [MagicMock() for _ in range(50)]
        sampled = self.analyzer._sample_keyframes(keyframes)
        assert len(sampled) == 50
        assert sampled == keyframes
    
    def test_sample_keyframes_large_session(self):
        """Test that large sessions (>150 keyframes) are sampled to 150"""
        keyframes = [MagicMock() for _ in range(300)]
        # Add timestamps to make them sortable
        for i, kf in enumerate(keyframes):
            kf.timestamp = datetime.now()
        
        sampled = self.analyzer._sample_keyframes(keyframes)
        assert len(sampled) == 150
        assert len(sampled) < len(keyframes)
    
    def test_prepare_analysis_data(self):
        """Test preparation of analysis data"""
        mock_keyframe = MagicMock()
        mock_keyframe.keyframe_type = "bottom"
        mock_keyframe.timestamp = datetime.now()
        mock_keyframe.pose_landmarks = json.dumps([
            {"name": "LEFT_HIP", "x": 100, "y": 200},
            {"name": "RIGHT_HIP", "x": 150, "y": 200}
        ])
        mock_keyframe.frame_data = "base64_data_here"
        
        analysis_data = self.analyzer._prepare_analysis_data([mock_keyframe], "squat")
        
        assert analysis_data["exercise"] == "squat"
        assert analysis_data["total_keyframes"] == 1
        assert len(analysis_data["keyframes"]) == 1
        assert analysis_data["keyframes"][0]["keyframe_type"] == "bottom"
        assert len(analysis_data["keyframes"][0]["landmarks"]) == 2
    
    def test_create_analysis_prompt(self):
        """Test prompt creation for Gemini"""
        analysis_data = {
            "exercise": "squat",
            "total_keyframes": 1,
            "keyframes": [{
                "keyframe_type": "bottom",
                "timestamp": "2024-01-01T10:00:00",
                "landmarks": [{"name": "LEFT_HIP", "x": 100, "y": 200}],
                "frame_preview": "base64..."
            }]
        }
        
        prompt = self.analyzer._create_analysis_prompt(analysis_data, "squat")
        
        assert "squat" in prompt
        assert "bottom" in prompt
        assert "LEFT_HIP" in prompt
        assert "JSON format" in prompt
        assert "overall_assessment" in prompt
    
    def test_parse_suggestions_valid_json(self):
        """Test parsing valid JSON suggestions"""
        json_response = '''
        {
            "overall_assessment": "Good form overall",
            "strengths": ["Consistent depth", "Good alignment"],
            "areas_for_improvement": ["Knee tracking", "Core engagement"],
            "specific_suggestions": [
                {
                    "category": "Posture",
                    "issue": "Knees caving in",
                    "suggestion": "Focus on pushing knees out",
                    "priority": "High"
                }
            ],
            "exercise_specific_tips": ["Keep chest up"],
            "next_session_focus": "Knee alignment"
        }
        '''
        
        suggestions = self.analyzer._parse_suggestions(json_response, "squat")
        
        assert suggestions["overall_assessment"] == "Good form overall"
        assert len(suggestions["strengths"]) == 2
        assert len(suggestions["areas_for_improvement"]) == 2
        assert len(suggestions["specific_suggestions"]) == 1
        assert suggestions["specific_suggestions"][0]["priority"] == "High"
    
    def test_parse_suggestions_invalid_json(self):
        """Test parsing invalid JSON suggestions"""
        text_response = "This is just plain text without JSON"
        
        suggestions = self.analyzer._parse_suggestions(text_response, "squat")
        
        assert suggestions["overall_assessment"] == "Analysis completed"
        assert "raw_response" in suggestions
        assert suggestions["raw_response"] == text_response
