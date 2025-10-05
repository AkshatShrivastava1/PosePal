import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.services.frame_processor import process_frame
from app.services.keyframe_detector import keyframe_detector


class TestFrameProcessor:
    """Test suite for frame processing functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a test image
        self.test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        self.test_image[:] = (100, 100, 100)  # Gray image
        
        # Mock MediaPipe pose landmarks (using actual landmark names)
        self.mock_landmarks = {
            'LEFT_SHOULDER': (100, 100),
            'RIGHT_SHOULDER': (200, 100),
            'LEFT_HIP': (100, 200),
            'RIGHT_HIP': (200, 200),
            'LEFT_KNEE': (100, 300),
            'RIGHT_KNEE': (200, 300),
            'LEFT_ANKLE': (100, 400),
            'RIGHT_ANKLE': (200, 400),
        }
        
        # Create mock landmark objects with .name attribute for the frame processor
        self.mock_landmark_objects = {}
        for name, coords in self.mock_landmarks.items():
            mock_landmark = Mock()
            mock_landmark.name = name
            self.mock_landmark_objects[name] = mock_landmark
    
    @patch('app.services.frame_processor.pose')
    def test_process_frame_with_pose_detection(self, mock_pose):
        """Test frame processing with successful pose detection"""
        # Mock MediaPipe pose results
        mock_results = Mock()
        mock_results.pose_landmarks = Mock()
        mock_pose.process.return_value = mock_results
        
        # Mock landmark coordinates function
        with patch('app.services.frame_processor.get_landmark_coordinates') as mock_get_coords:
            mock_get_coords.return_value = self.mock_landmarks
            
            # Mock the keyframe detector to avoid landmark conversion issues
            with patch.object(keyframe_detector, 'should_save_keyframe') as mock_detector:
                mock_detector.return_value = (None, False)
                
                with patch.object(keyframe_detector, 'get_rep_count') as mock_rep_count:
                    mock_rep_count.return_value = 0
                    
                    result = process_frame(self.test_image, session_id=1, exercise='squat')
                    
                    # Verify pose processing was called
                    mock_pose.process.assert_called_once()
                    mock_get_coords.assert_called_once()
                    
                    # Verify result structure
                    assert 'landmarks' in result
                    assert 'annotated_image' in result
                    assert 'keyframe_type' in result
                    assert 'should_save_keyframe' in result
                    assert 'rep_completed' in result
                    assert 'current_rep_count' in result
                    
                    # Verify landmarks are returned
                    assert result['landmarks'] == self.mock_landmarks
                    
                    # Verify annotated image is base64 encoded
                    assert isinstance(result['annotated_image'], str)
                    assert result['annotated_image'].startswith('/9j/')  # JPEG base64 starts with this
    
    @patch('app.services.frame_processor.pose')
    def test_process_frame_no_pose_detected(self, mock_pose):
        """Test frame processing when no pose is detected"""
        # Mock MediaPipe pose results with no pose
        mock_results = Mock()
        mock_results.pose_landmarks = None
        mock_pose.process.return_value = mock_results
        
        # Mock landmark coordinates function
        with patch('app.services.frame_processor.get_landmark_coordinates') as mock_get_coords:
            mock_get_coords.return_value = {}
            
            result = process_frame(self.test_image, session_id=1, exercise='squat')
            
            # Verify result structure
            assert 'landmarks' in result
            assert 'annotated_image' in result
            assert 'keyframe_type' in result
            assert 'should_save_keyframe' in result
            assert 'rep_completed' in result
            assert 'current_rep_count' in result
            
            # Verify landmarks are empty
            assert result['landmarks'] == {}
            
            # Verify no keyframe or rep completion
            assert result['keyframe_type'] is None
            assert result['should_save_keyframe'] == False
            assert result['rep_completed'] == False
            assert result['current_rep_count'] == 0
    
    @patch('app.services.frame_processor.pose')
    def test_process_frame_with_keyframe_detection(self, mock_pose):
        """Test frame processing with keyframe detection"""
        # Mock MediaPipe pose results
        mock_results = Mock()
        mock_results.pose_landmarks = Mock()
        mock_pose.process.return_value = mock_results
        
        # Mock landmark coordinates function
        with patch('app.services.frame_processor.get_landmark_coordinates') as mock_get_coords:
            mock_get_coords.return_value = self.mock_landmarks
            
            # Mock keyframe detector
            with patch.object(keyframe_detector, 'should_save_keyframe') as mock_detector:
                mock_detector.return_value = ('bottom', True)  # keyframe_type, rep_completed
                
                with patch.object(keyframe_detector, 'get_rep_count') as mock_rep_count:
                    mock_rep_count.return_value = 5
                    
                    result = process_frame(self.test_image, session_id=1, exercise='squat')
                    
                    # Debug: print the result to see what's happening
                    print("Result:", result)
                    
                    # Verify keyframe detector was called
                    mock_detector.assert_called_once()
                    mock_rep_count.assert_called_once_with(1)
                    
                    # Verify result
                    assert result['keyframe_type'] == 'bottom'
                    assert result['should_save_keyframe'] == True
                    assert result['rep_completed'] == True
                    assert result['current_rep_count'] == 5
    
    def test_process_frame_no_session_id(self):
        """Test frame processing without session_id"""
        with patch('app.services.frame_processor.pose') as mock_pose:
            mock_results = Mock()
            mock_results.pose_landmarks = Mock()
            mock_pose.process.return_value = mock_results
            
            with patch('app.services.frame_processor.get_landmark_coordinates') as mock_get_coords:
                mock_get_coords.return_value = self.mock_landmarks
                
                result = process_frame(self.test_image, session_id=None, exercise='squat')
                
                # Verify no keyframe detection when no session_id
                assert result['keyframe_type'] is None
                assert result['should_save_keyframe'] == False
                assert result['rep_completed'] == False
                assert result['current_rep_count'] == 0
    
    def test_process_frame_error_handling(self):
        """Test frame processing error handling"""
        # Test with invalid image
        invalid_image = "not_an_image"
        
        result = process_frame(invalid_image, session_id=1, exercise='squat')
        
        # Verify error handling
        assert 'error' in result
        assert result['landmarks'] is None
        assert result['keyframe_type'] is None
        assert result['should_save_keyframe'] == False
        assert result['rep_completed'] == False
        assert result['current_rep_count'] == 0
    
    @patch('app.services.frame_processor.pose')
    def test_process_frame_different_exercises(self, mock_pose):
        """Test frame processing with different exercise types"""
        # Mock MediaPipe pose results
        mock_results = Mock()
        mock_results.pose_landmarks = Mock()
        mock_pose.process.return_value = mock_results
        
        # Mock landmark coordinates function
        with patch('app.services.frame_processor.get_landmark_coordinates') as mock_get_coords:
            mock_get_coords.return_value = self.mock_landmarks
            
            # Test different exercises
            exercises = ['squat', 'pushup', 'lunges', 'plank']
            
            for exercise in exercises:
                with patch.object(keyframe_detector, 'should_save_keyframe') as mock_detector:
                    mock_detector.return_value = (None, False)
                    
                    result = process_frame(self.test_image, session_id=1, exercise=exercise)
                    
                    # Verify detector was called with correct exercise
                    mock_detector.assert_called_once()
                    call_args = mock_detector.call_args[0]
                    assert call_args[1] == exercise  # exercise parameter
    
    @patch('app.services.frame_processor.pose')
    def test_process_frame_landmark_conversion(self, mock_pose):
        """Test that landmarks are properly converted for keyframe detector"""
        # Mock MediaPipe pose results
        mock_results = Mock()
        mock_results.pose_landmarks = Mock()
        mock_pose.process.return_value = mock_results
        
        # Mock landmark coordinates function
        with patch('app.services.frame_processor.get_landmark_coordinates') as mock_get_coords:
            mock_get_coords.return_value = self.mock_landmarks
            
            with patch.object(keyframe_detector, 'should_save_keyframe') as mock_detector:
                mock_detector.return_value = (None, False)
                
                process_frame(self.test_image, session_id=1, exercise='squat')
                
                # Verify detector was called with converted landmarks
                mock_detector.assert_called_once()
                call_args = mock_detector.call_args[0]
                landmarks_list = call_args[2]  # landmarks parameter
                
                # Verify landmarks are converted to list format
                assert isinstance(landmarks_list, list)
                assert len(landmarks_list) == len(self.mock_landmarks)
                
                # Verify each landmark has correct structure
                for landmark in landmarks_list:
                    assert 'name' in landmark
                    assert 'x' in landmark
                    assert 'y' in landmark
                    assert isinstance(landmark['x'], (int, float))
                    assert isinstance(landmark['y'], (int, float))


class TestFrameProcessorIntegration:
    """Integration tests for frame processor with keyframe detector"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        self.test_image[:] = (100, 100, 100)
        
        # Reset keyframe detector state
        keyframe_detector.reset_session(1)
    
    @patch('app.services.frame_processor.pose')
    def test_squat_rep_counting_integration(self, mock_pose):
        """Test integration of frame processor with squat rep counting"""
        # Mock MediaPipe pose results
        mock_results = Mock()
        mock_results.pose_landmarks = Mock()
        mock_pose.process.return_value = mock_results
        
        # Mock landmark coordinates for different phases
        bottom_landmarks = {'LEFT_HIP': (100, 200)}
        top_landmarks = {'LEFT_HIP': (100, 100)}
        
        with patch('app.services.frame_processor.get_landmark_coordinates') as mock_get_coords:
            # First frame - bottom position
            mock_get_coords.return_value = bottom_landmarks
            result1 = process_frame(self.test_image, session_id=1, exercise='squat')
            
            # Second frame - top position
            mock_get_coords.return_value = top_landmarks
            result2 = process_frame(self.test_image, session_id=1, exercise='squat')
            
            # Verify rep counting worked
            assert result1['rep_completed'] == False
            assert result2['rep_completed'] == True
            assert result2['current_rep_count'] == 1
    
    @patch('app.services.frame_processor.pose')
    def test_plank_keyframe_integration(self, mock_pose):
        """Test integration of frame processor with plank keyframe detection"""
        # Mock MediaPipe pose results
        mock_results = Mock()
        mock_results.pose_landmarks = Mock()
        mock_pose.process.return_value = mock_results
        
        with patch('app.services.frame_processor.get_landmark_coordinates') as mock_get_coords:
            mock_get_coords.return_value = {}
            
            # First call should return keyframe
            result1 = process_frame(self.test_image, session_id=1, exercise='plank')
            assert result1['keyframe_type'] == 'plank_interval'
            assert result1['rep_completed'] == False
            
            # Second call within 30 seconds should not return keyframe
            result2 = process_frame(self.test_image, session_id=1, exercise='plank')
            assert result2['keyframe_type'] is None
            assert result2['rep_completed'] == False
