import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

class KeyframeDetector:
    def __init__(self):
        self.last_keyframe_time = {}  # Track last keyframe time per session
        self.motion_state = {}  # Track motion state per session
        self.last_landmarks = {}  # Track previous landmarks for motion detection
        self.rep_counters = {}  # Track rep counting per session
        
    def should_save_keyframe(
        self, 
        session_id: int, 
        exercise: str, 
        landmarks: List[Dict], 
        timestamp: datetime
    ) -> Tuple[Optional[str], bool]:
        """
        Determine if current frame should be saved as a keyframe and if a rep was completed.
        Returns (keyframe_type, rep_completed)
        """
        if exercise == 'plank':
            keyframe_type = self._check_plank_keyframe(session_id, timestamp)
            return keyframe_type, False  # Planks don't count reps
        else:
            return self._check_motion_keyframe(session_id, exercise, landmarks, timestamp)
    
    def _check_plank_keyframe(self, session_id: int, timestamp: datetime) -> Optional[str]:
        """Check if plank interval keyframe should be saved (every 30 seconds)"""
        if session_id not in self.last_keyframe_time:
            self.last_keyframe_time[session_id] = timestamp
            return 'plank_interval'
        
        time_diff = timestamp - self.last_keyframe_time[session_id]
        if time_diff >= timedelta(seconds=10):
            self.last_keyframe_time[session_id] = timestamp
            print(f"🔍 [PLANK KEYFRAME] Session {session_id}: 10-second interval keyframe detected")
            return 'plank_interval'
        
        return None
    
    def _check_motion_keyframe(
        self, 
        session_id: int, 
        exercise: str, 
        landmarks: List[Dict], 
        timestamp: datetime
    ) -> Tuple[Optional[str], bool]:
        """Check if motion-based keyframe should be saved and if rep was completed"""
        
        if not landmarks:
            return None, False
            
        # Initialize session state if needed
        if session_id not in self.motion_state:
            self.motion_state[session_id] = {
                'last_phase': 'unknown',
                'last_keyframe_time': timestamp,
                'last_landmarks': landmarks
            }
            self.rep_counters[session_id] = {
                'current_rep_phases': set(),  # Track phases in current rep
                'total_reps': 0,
                'last_complete_rep_time': None
            }
            return 'middle', False  # Save first frame
        
        session_state = self.motion_state[session_id]
        rep_counter = self.rep_counters[session_id]
        
        # Detect current phase based on exercise
        current_phase = self._detect_motion_phase(exercise, landmarks, session_state['last_landmarks'])
        
        # Check if we should save a keyframe
        keyframe_type = None
        rep_completed = False
        
        if exercise in ['squat', 'lunges', 'pushup']:
            # For exercises that count reps: save at bottom, top, and middle transitions
            if current_phase != session_state['last_phase']:
                print(f"🔍 [PHASE DEBUG] Session {session_id}: phase changed from {session_state['last_phase']} to {current_phase}")
                
                if current_phase == 'bottom':
                    keyframe_type = 'bottom'
                    rep_counter['current_rep_phases'].add('bottom')
                    print(f"🔍 [KEYFRAME IDENTIFIED] Session {session_id}: BOTTOM keyframe detected")
                    print(f"🔍 [REP PROGRESS] Session {session_id}: current phases = {rep_counter['current_rep_phases']}")
                    
                elif current_phase == 'top':
                    keyframe_type = 'top'
                    rep_counter['current_rep_phases'].add('top')
                    print(f"🔍 [KEYFRAME IDENTIFIED] Session {session_id}: TOP keyframe detected")
                    print(f"🔍 [REP PROGRESS] Session {session_id}: current phases = {rep_counter['current_rep_phases']}")
                    
                    # Check if rep is complete (has both bottom and top)
                    if 'bottom' in rep_counter['current_rep_phases'] and 'top' in rep_counter['current_rep_phases']:
                        rep_completed = True
                        rep_counter['total_reps'] += 1
                        print(f"🎉 [REP COUNTED] Session {session_id}: REP #{rep_counter['total_reps']} COMPLETED!")
                        rep_counter['current_rep_phases'].clear()  # Reset for next rep
                        rep_counter['last_complete_rep_time'] = timestamp
                        
                elif current_phase == 'middle' and session_state['last_phase'] != 'unknown':
                    keyframe_type = 'middle'
                    print(f"🔍 [KEYFRAME IDENTIFIED] Session {session_id}: MIDDLE keyframe detected")
        
        # Update session state
        session_state['last_phase'] = current_phase
        session_state['last_landmarks'] = landmarks
        
        return keyframe_type, rep_completed
    
    def _detect_motion_phase(self, exercise: str, landmarks: List[Dict], last_landmarks: List[Dict]) -> str:
        """Detect current phase of motion based on landmarks"""
        
        if not landmarks or not last_landmarks:
            return 'unknown'
        
        try:
            if exercise in ['squat', 'lunges']:
                return self._detect_squat_phase(landmarks, last_landmarks)
            elif exercise == 'pushup':
                return self._detect_pushup_phase(landmarks, last_landmarks)
            else:
                return 'middle'
        except Exception:
            return 'unknown'
    
    def _detect_squat_phase(self, landmarks: List[Dict], last_landmarks: List[Dict]) -> str:
        """Detect squat phase based on hip and knee positions"""
        
        # This is a simplified detection - in real implementation you'd use MediaPipe landmarks
        
        # For demo purposes, simulate phase detection
        # In real implementation, you'd analyze:
        # - Hip height relative to knees
        # - Knee angles
        # - Movement direction (up/down)
        
        # Simulate based on some landmark analysis
        hip_y = self._get_landmark_y(landmarks, 'LEFT_HIP')
        knee_y = self._get_landmark_y(landmarks, 'LEFT_KNEE')
        
        print(f"🔍 [LANDMARK DEBUG] LEFT_HIP y={hip_y}, LEFT_KNEE y={knee_y}")
        
        if hip_y is None or knee_y is None:
            print(f"🔍 [LANDMARK DEBUG] Missing landmarks - returning 'unknown'")
            return 'unknown'
        
        # Simple heuristic: if hip is significantly below knee, it's bottom
        if hip_y > knee_y + 0.05:  # Adjust threshold as needed
            print(f"🔍 [LANDMARK DEBUG] Hip below knee - returning 'bottom'")
            return 'bottom'
        elif hip_y < knee_y - 0.05:
            print(f"🔍 [LANDMARK DEBUG] Hip above knee - returning 'top'")
            return 'top'
        else:
            print(f"🔍 [LANDMARK DEBUG] Hip at knee level - returning 'middle'")
            return 'middle'
    
    def _detect_pushup_phase(self, landmarks: List[Dict], last_landmarks: List[Dict]) -> str:
        """Detect push-up phase based on shoulder position relative to elbows"""
        
        shoulder_y = self._get_landmark_y(landmarks, 'LEFT_SHOULDER')
        elbow_y = self._get_landmark_y(landmarks, 'LEFT_ELBOW')
        
        if shoulder_y is None or elbow_y is None:
            return 'unknown'
        
        # Calculate the difference between shoulder and elbow Y positions
        # Positive values = shoulders below elbows (bottom position)
        # Negative values = shoulders above elbows (top position)
        shoulder_elbow_diff = shoulder_y - elbow_y
        
        print(f"🔍 [PUSHUP DEBUG] shoulder_y={shoulder_y:.3f}, elbow_y={elbow_y:.3f}, diff={shoulder_elbow_diff:.3f}")
        
        # Use 0.05 threshold as suggested
        if shoulder_elbow_diff > 0.05:  # Shoulders significantly below elbows (bottom)
            return 'bottom'
        elif shoulder_elbow_diff < -0.05:  # Shoulders significantly above elbows (top)
            return 'top'
        else:
            return 'middle'
    
    def _get_landmark_y(self, landmarks: List[Dict], landmark_name: str) -> Optional[float]:
        """Extract Y coordinate for a specific landmark"""
        
        # Look for the landmark by name
        for landmark in landmarks:
            if landmark.get('name') == landmark_name:
                y_coord = landmark.get('y')
                print(f"🔍 [LANDMARK LOOKUP] Found {landmark_name}: y={y_coord}")
                return y_coord
        
        print(f"🔍 [LANDMARK LOOKUP] {landmark_name} not found in {len(landmarks)} landmarks")
        return None
    
    def get_rep_count(self, session_id: int) -> int:
        """Get current rep count for a session"""
        if session_id in self.rep_counters:
            return self.rep_counters[session_id]['total_reps']
        return 0
    
    def reset_session(self, session_id: int):
        """Reset tracking state for a session"""
        if session_id in self.motion_state:
            del self.motion_state[session_id]
        if session_id in self.last_keyframe_time:
            del self.last_keyframe_time[session_id]
        if session_id in self.rep_counters:
            del self.rep_counters[session_id]

# Global instance
keyframe_detector = KeyframeDetector()
