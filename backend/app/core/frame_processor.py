import cv2
import math as m
import mediapipe as mp

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

# Initilize frame counters.
good_frames = 0
bad_frames = 0

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

'''
def annotate_image(image, lm, lmPose, w, h):
    # Check if pose landmarks are detected
    if lm is not None:
        # Acquire the landmark coordinates.
        # Once aligned properly, left or right should not be a concern.      
        # Left shoulder.
        l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * w)
        l_shldr_y = int(lm.landmark[lmPose.LEFT_SHOULDER].y * h)
        # Right shoulder
        r_shldr_x = int(lm.landmark[lmPose.RIGHT_SHOULDER].x * w)
        r_shldr_y = int(lm.landmark[lmPose.RIGHT_SHOULDER].y * h)
        # Left ear.
        l_ear_x = int(lm.landmark[lmPose.LEFT_EAR].x * w)
        l_ear_y = int(lm.landmark[lmPose.LEFT_EAR].y * h)
        # Left hip.
        l_hip_x = int(lm.landmark[lmPose.LEFT_HIP].x * w)
        l_hip_y = int(lm.landmark[lmPose.LEFT_HIP].y * h)
    else:
        # No pose detected - skip this frame
        cv2.putText(image, 'No pose detected - Position yourself in frame', (10, 30), font, 0.9, red, 2)
        return image

    # Calculate distance between left shoulder and right shoulder points.
    offset = findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)

    # Assist to align the camera to point at the side view of the person.
    # Offset threshold 30 is based on results obtained from analysis over 100 samples.
    if offset < 100:
        cv2.putText(image, str(int(offset)) + ' Aligned', (w - 150, 30), font, 0.9, green, 2)
    else:
        cv2.putText(image, str(int(offset)) + ' Not Aligned', (w - 150, 30), font, 0.9, red, 2)

    # Calculate angles.
    neck_inclination = findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
    torso_inclination = findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

    # Draw landmarks.
    cv2.circle(image, (l_shldr_x, l_shldr_y), 7, yellow, -1)
    cv2.circle(image, (l_ear_x, l_ear_y), 7, yellow, -1)

    # Let's take y - coordinate of P3 100px above x1,  for display elegance.
    # Although we are taking y = 0 while calculating angle between P1,P2,P3.
    cv2.circle(image, (l_shldr_x, l_shldr_y - 100), 7, yellow, -1)
    cv2.circle(image, (r_shldr_x, r_shldr_y), 7, pink, -1)
    cv2.circle(image, (l_hip_x, l_hip_y), 7, yellow, -1)

    # Similarly, here we are taking y - coordinate 100px above x1. Note that
    # you can take any value for y, not necessarily 100 or 200 pixels.
    cv2.circle(image, (l_hip_x, l_hip_y - 100), 7, yellow, -1)

    cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), red, 4)

    return image

'''