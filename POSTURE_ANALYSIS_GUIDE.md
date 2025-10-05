# PosePal - AI-Powered Posture Analysis System

## Overview

PosePal is a comprehensive fitness application that uses computer vision and AI to analyze workout form and provide personalized posture improvement suggestions. The system combines MediaPipe pose detection with Google's Gemini AI to deliver professional-grade fitness coaching.

## Key Features

- **Real-time Pose Detection**: Uses MediaPipe to track 33 body landmarks during workouts
- **Exercise-Specific Analysis**: Supports squats, push-ups, lunges, and planks
- **AI-Powered Suggestions**: Leverages Gemini AI for professional posture analysis
- **Keyframe Storage**: Captures significant moments during exercises
- **Rep Counting**: Automatically counts repetitions for motion-based exercises
- **Session Management**: Complete workout session tracking and analysis

## Architecture

### Backend (FastAPI + Python)
- **Frame Processing**: Real-time pose detection and annotation
- **Keyframe Detection**: Identifies significant exercise phases
- **AI Analysis**: Gemini-powered posture analysis
- **Data Management**: SQLite database with session and keyframe storage

### Frontend (React + TypeScript)
- **Camera Integration**: Real-time video capture and display
- **Workout Interface**: Exercise selection and session management
- **Progress Tracking**: Real-time rep counting and session metrics

## API Endpoints

### Session Management
- `POST /sessions/start` - Start a new workout session
- `POST /sessions/{session_id}/stop` - End a workout session
- `GET /sessions/{session_id}/summary` - Get session summary

### Frame Processing
- `POST /frames/{session_id}` - Process video frames for pose detection

### Posture Analysis
- `POST /analysis/analyze` - Analyze session posture with Gemini AI
- `POST /analysis/cleanup/{session_id}` - Delete session data after analysis
- `POST /analysis/analyze-and-cleanup/{session_id}` - Combined analysis and cleanup
- `GET /analysis/{session_id}/keyframes/count` - Get keyframe count for session

### Keyframe Management
- `POST /keyframes` - Store a keyframe
- `GET /keyframes/sessions/{session_id}` - Get keyframes for a session
- `DELETE /keyframes/sessions/{session_id}` - Clear keyframes for a session

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API key

### Backend Setup
1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key_here"
   ```

3. Initialize database:
   ```bash
   python -c "from app.db.database import create_db_and_tables; create_db_and_tables()"
   ```

4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Install dependencies:
   ```bash
   cd frontend-react
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

## Usage Workflow

### 1. Start a Workout Session
```bash
curl -X POST "http://localhost:8000/sessions/start" \
  -H "Content-Type: application/json" \
  -d '{"exercise": "squat", "user_id": 1}'
```

### 2. Process Video Frames
The frontend automatically sends frames to `/frames/{session_id}` during the workout.

### 3. End the Session
```bash
curl -X POST "http://localhost:8000/sessions/{session_id}/stop" \
  -H "Content-Type: application/json" \
  -d '{"ts": "2024-01-15T10:30:00Z"}'
```

### 4. Analyze Posture and Clean Up
```bash
curl -X POST "http://localhost:8000/analysis/analyze-and-cleanup/{session_id}"
```

## Data Flow

1. **Frame Capture**: Frontend captures video frames from camera
2. **Pose Detection**: Backend processes frames with MediaPipe
3. **Keyframe Storage**: Significant frames are stored with pose data
4. **Session End**: User stops the workout session
5. **AI Analysis**: Gemini analyzes keyframes and generates suggestions
6. **Data Cleanup**: Session data is deleted after analysis

## Keyframe Sampling

For sessions with more than 150 keyframes, the system automatically samples an evenly distributed subset to optimize AI analysis performance while maintaining representative data coverage.

## Exercise-Specific Features

### Squats, Push-ups, Lunges
- **Rep Counting**: Automatically counts completed repetitions
- **Phase Detection**: Identifies bottom, top, and middle positions
- **Form Analysis**: Analyzes alignment and movement patterns

### Planks
- **Time-based Keyframes**: Captures frames every 30 seconds
- **Stability Analysis**: Evaluates core engagement and alignment
- **Duration Tracking**: Monitors hold time and consistency

## AI Analysis Features

The Gemini AI provides:
- **Overall Assessment**: Comprehensive session evaluation
- **Strengths Identification**: Highlights good form elements
- **Improvement Areas**: Identifies specific issues
- **Actionable Suggestions**: Detailed improvement recommendations
- **Exercise-Specific Tips**: Targeted advice for each exercise type
- **Next Session Focus**: Guidance for future workouts

## Database Schema

### Sessions
- Session metadata (exercise, duration, timestamps)
- User association
- Start/end times

### Keyframes
- Annotated images with pose overlays
- Pose landmark coordinates
- Keyframe type (bottom/top/middle/plank_interval)
- Exercise context

### Metrics
- Rep counts
- Duration tracking
- Performance flags

## Security Considerations

- **API Key Management**: Gemini API key stored in environment variables
- **Data Privacy**: Session data deleted after analysis
- **CORS Configuration**: Properly configured for frontend-backend communication

## Performance Optimization

- **Keyframe Sampling**: Reduces data volume for large sessions
- **Efficient Storage**: Base64 encoding for image data
- **Batch Processing**: Optimized database operations
- **Real-time Processing**: 100ms frame processing intervals

## Testing

Run the test suite:
```bash
cd backend
pytest tests/ -v
```

Key test areas:
- Frame processing accuracy
- Keyframe detection logic
- AI analysis integration
- Database operations
- API endpoint functionality

## Troubleshooting

### Common Issues
1. **Gemini API Errors**: Verify API key and quota limits
2. **Camera Access**: Ensure proper browser permissions
3. **Database Errors**: Check SQLite file permissions
4. **CORS Issues**: Verify frontend-backend URL configuration

### Debug Mode
Enable detailed logging by setting environment variables:
```bash
export DEBUG=true
export LOG_LEVEL=debug
```

## Future Enhancements

- **Multi-exercise Sessions**: Support for circuit training
- **Progress Tracking**: Historical analysis and trends
- **Social Features**: Share achievements and compete with friends
- **Mobile App**: Native iOS/Android applications
- **Advanced Analytics**: Machine learning model improvements
