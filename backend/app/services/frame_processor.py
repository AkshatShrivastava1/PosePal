import cv2
import math as m
import mediapipe as mp
import json
from datetime import datetime
from app.services.keyframe_detector import keyframe_detector

# Calculate distance
def findDistance(x1, y1, x2, y2):
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist

# Calculate angle.
def findAngle(x1, y1, x2, y2):
    theta = m.acos((y2 - y1) * (-y1) / (m.sqrt(
        (x2 - x1) ** 2 + (y2 - y1) ** 2) * y1))
    degree = int(180 / m.pi) * theta
    return degree

# Font type.
font = cv2.FONT_HERSHEY_SIMPLEX

# Colors.
blue = (255, 127, 0)
red = (50, 50, 255)
green = (127, 255, 0)
dark_blue = (127, 20, 0)
light_green = (127, 233, 100)
yellow = (0, 255, 255)
pink = (255, 0, 255)

# Initialize mediapipe pose class.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
lmPose = mp_pose.PoseLandmark

LANDMARKS_OF_INTEREST = [
            lmPose.LEFT_SHOULDER, lmPose.RIGHT_SHOULDER,
            lmPose.LEFT_HIP, lmPose.RIGHT_HIP,
            lmPose.LEFT_KNEE, lmPose.RIGHT_KNEE,
            lmPose.LEFT_ANKLE, lmPose.RIGHT_ANKLE,
            lmPose.LEFT_HEEL, lmPose.RIGHT_HEEL,
            lmPose.LEFT_FOOT_INDEX, lmPose.RIGHT_FOOT_INDEX,
            lmPose.LEFT_ELBOW, lmPose.RIGHT_ELBOW,
            lmPose.LEFT_WRIST, lmPose.RIGHT_WRIST,
            lmPose.LEFT_INDEX, lmPose.RIGHT_INDEX
        ]

def get_landmark_coordinates(keypoints, w, h):
    landmarks = {}
    lm = keypoints.pose_landmarks
    if lm is not None:
        for landmark_name in LANDMARKS_OF_INTEREST:
            landmark = lm.landmark[landmark_name]
            landmarks[landmark_name] = (int(landmark.x * w), int(landmark.y * h))
    return landmarks

def annotate_image(image, landmark_coordinates, w, h):
    # Use lm and lmPose as representative of the following methods.
    lm = landmark_coordinates
    # Check if pose landmarks are detected
    if lm is not None:
        # Draw skeleton connections
        skeleton_connections = [
            # Shoulder to shoulder (left to right)
            (lmPose.LEFT_SHOULDER, lmPose.RIGHT_SHOULDER, blue),
            
            # Shoulders to hips
            (lmPose.LEFT_SHOULDER, lmPose.LEFT_HIP, green),
            (lmPose.RIGHT_SHOULDER, lmPose.RIGHT_HIP, green),

            # Hips to Hips
            (lmPose.LEFT_HIP, lmPose.RIGHT_HIP, green),
            
            # Hips to knees
            (lmPose.LEFT_HIP, lmPose.LEFT_KNEE, green),
            (lmPose.RIGHT_HIP, lmPose.RIGHT_KNEE, green),
            
            # Knees to ankles
            (lmPose.LEFT_KNEE, lmPose.LEFT_ANKLE, green),
            (lmPose.RIGHT_KNEE, lmPose.RIGHT_ANKLE, green),
            
            # Ankles to heels
            (lmPose.LEFT_ANKLE, lmPose.LEFT_HEEL, pink),
            (lmPose.RIGHT_ANKLE, lmPose.RIGHT_HEEL, pink),
            
            # Ankles to feet (foot index)
            (lmPose.LEFT_ANKLE, lmPose.LEFT_FOOT_INDEX, pink),
            (lmPose.RIGHT_ANKLE, lmPose.RIGHT_FOOT_INDEX, pink),
            
            # Shoulder to elbows
            (lmPose.LEFT_SHOULDER, lmPose.LEFT_ELBOW, yellow),
            (lmPose.RIGHT_SHOULDER, lmPose.RIGHT_ELBOW, yellow),
            
            # Elbows to wrists
            (lmPose.LEFT_ELBOW, lmPose.LEFT_WRIST, yellow),
            (lmPose.RIGHT_ELBOW, lmPose.RIGHT_WRIST, yellow),
            
            # Wrists to index fingers
            (lmPose.LEFT_WRIST, lmPose.LEFT_INDEX, red),
            (lmPose.RIGHT_WRIST, lmPose.RIGHT_INDEX, red)
        ]
        
        # Draw all skeleton lines
        for start_point, end_point, color in skeleton_connections:
            if start_point in lm and end_point in lm:
                cv2.line(image, lm[start_point], lm[end_point], color, 3)
        
        # Draw landmark points
        for landmark_name, (x, y) in lm.items():
            cv2.circle(image, (x, y), 5, yellow, -1)
            
    else:
        # No pose detected - skip this frame
        cv2.putText(image, 'No pose detected - Position yourself in frame', (10, 30), font, 0.9, red, 2)
    return image

def process_frame(image, session_id=None, exercise='squat'):
    """
    Process a single frame for pose detection and analysis
    Returns pose landmarks and analysis results
    """
    print(f"🔍 [FRAME PROCESS START] Session {session_id}: Processing frame")
    try:
        # Get image dimensions
        h, w = image.shape[:2]
        print(f"🔍 [FRAME PROCESS] Session {session_id}: Image dimensions {w}x{h}")
        
        # Convert BGR to RGB for MediaPipe
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image with MediaPipe
        results = pose.process(rgb_image)
        print(f"🔍 [MEDIAPIPE] Session {session_id}: MediaPipe processed frame")
        
        # Get landmark coordinates
        landmarks = get_landmark_coordinates(results, w, h)
        print(f"🔍 [LANDMARKS] Session {session_id}: Got {len(landmarks) if landmarks else 0} landmarks")
        
        # Annotate the image with pose landmarks
        annotated_image = annotate_image(image.copy(), landmarks, w, h)
        
        # Convert annotated image back to base64 for response
        import base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Check if this should be saved as a keyframe and if rep was completed
        keyframe_type = None
        rep_completed = False
        if session_id is not None:
            # Convert landmarks to list format for keyframe detector
            landmarks_list = []
            if landmarks:
                for landmark_name, (x, y) in landmarks.items():
                    landmarks_list.append({
                        'name': landmark_name.name,
                        'x': x / w,  # Normalize coordinates to 0-1 range
                        'y': y / h   # Normalize coordinates to 0-1 range
                    })
            
            print(f"🔍 [POSE DEBUG] Session {session_id}: {len(landmarks)} landmarks detected")
            if landmarks_list:
                print(f"🔍 [POSE DEBUG] Sample landmarks: {landmarks_list[:3]}")
            
            keyframe_type, rep_completed = keyframe_detector.should_save_keyframe(
                session_id, exercise, landmarks_list, datetime.now()
            )
            
            print(f"🔍 [KEYFRAME DEBUG] Session {session_id}: keyframe_type={keyframe_type}, rep_completed={rep_completed}")
            print(f"🔍 [REP DEBUG] Session {session_id}: current_rep_count={keyframe_detector.get_rep_count(session_id)}")
        
        # Extract pose analysis data
        pose_data = {
            'landmarks': landmarks,
            'annotated_image': annotated_base64,
            'keyframe_type': keyframe_type,
            'should_save_keyframe': keyframe_type is not None,
            'rep_completed': rep_completed,
            'current_rep_count': keyframe_detector.get_rep_count(session_id) if session_id else 0
        }
        
        return pose_data
        
    except Exception as e:
        print(f"❌ [FRAME PROCESS ERROR] Session {session_id}: {str(e)}")
        return {
            'error': str(e),
            'landmarks': None,
            'keyframe_type': None,
            'should_save_keyframe': False,
            'rep_completed': False,
            'current_rep_count': 0
        }